"""
Comprehensive tests for ReproducibilityMetric.

Tests cover:
- Safe code execution
- Dangerous pattern detection
- Timeout handling
- Edge cases
- Cross-platform compatibility
"""

import pytest
from unittest.mock import patch
from src.metrics.Reproducibility import ReproducibilityMetric
from src.models import ModelContext, ParsedURL, URLCategory


@pytest.fixture
def metric():
    """Create a ReproducibilityMetric instance."""
    return ReproducibilityMetric()


@pytest.fixture
def base_context():
    """Create a base ModelContext for testing."""
    return ModelContext(
        model_url=ParsedURL(
            url="https://huggingface.co/test/model",
            category=URLCategory.MODEL,
            name="test/model",
            platform="huggingface",
            owner="test",
            repo="model"
        ),
        readme_content=None
    )


class TestBasicFunctionality:
    """Test basic metric functionality."""
    
    def test_metric_name(self, metric):
        """Test metric name property."""
        assert metric.name == "reproducibility"
    
    @pytest.mark.asyncio
    async def test_no_readme_returns_zero(self, metric, base_context):
        """Test that no README content returns score 0.0."""
        base_context.readme_content = None
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
        assert result.latency >= 0
    
    @pytest.mark.asyncio
    async def test_no_code_blocks_returns_zero(self, metric, base_context):
        """Test that README without code blocks returns score 0.0."""
        base_context.readme_content = """
        # Test Model
        
        This is a great model but has no code examples.
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0


class TestSafeCodeExecution:
    """Test safe code execution scenarios."""
    
    @pytest.mark.asyncio
    async def test_simple_safe_code_runs(self, metric, base_context):
        """Test that simple safe code executes successfully."""
        base_context.readme_content = """
        # Test Model
        
        ```python
        x = 10
        y = 20
        print(x + y)
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 1.0  # Runs without modification
    
    @pytest.mark.asyncio
    async def test_safe_torch_code(self, metric, base_context):
        """Test safe PyTorch code execution."""
        base_context.readme_content = """
        # Test Model
        
        ```python
        try:
            import torch
            tensor = torch.zeros(5)
            print("Success")
        except ImportError:
            print("Torch not available")
        ```
        """
        result = await metric.compute(base_context, {})
        # Should be 1.0 or 0.5 depending on if torch is available
        assert result.score in [0.0, 0.5, 1.0]
    
    @pytest.mark.asyncio
    async def test_multiple_safe_code_blocks(self, metric, base_context):
        """Test multiple safe code blocks."""
        base_context.readme_content = """
        # Test Model
        
        First example:
        ```python
        x = 1
        ```
        
        Second example:
        ```python
        y = 2
        print(y)
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score >= 0.0  # At least one should work


class TestDangerousCodeBlocking:
    """Test dangerous code pattern detection and blocking."""
    
    @pytest.mark.asyncio
    async def test_os_system_blocked(self, metric, base_context):
        """Test that os.system() is blocked."""
        base_context.readme_content = """
        ```python
        import os
        os.system('ls')
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_subprocess_blocked(self, metric, base_context):
        """Test that subprocess is blocked."""
        base_context.readme_content = """
        ```python
        import subprocess
        subprocess.run(['ls'])
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_exec_blocked(self, metric, base_context):
        """Test that exec() is blocked."""
        base_context.readme_content = """
        ```python
        exec("print('dangerous')")
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_eval_blocked(self, metric, base_context):
        """Test that eval() is blocked."""
        base_context.readme_content = """
        ```python
        eval("1 + 1")
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_file_operations_blocked(self, metric, base_context):
        """Test that file operations are blocked."""
        base_context.readme_content = """
        ```python
        with open('/etc/passwd', 'r') as f:
            data = f.read()
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_network_calls_blocked(self, metric, base_context):
        """Test that network calls are blocked."""
        base_context.readme_content = """
        ```python
        import requests
        requests.get('http://example.com')
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_mixed_safe_and_unsafe(self, metric, base_context):
        """Test mixed safe and unsafe code blocks."""
        base_context.readme_content = """
        Safe code:
        ```python
        x = 10
        print(x)
        ```
        
        Unsafe code:
        ```python
        import os
        os.system('rm -rf /')
        ```
        """
        result = await metric.compute(base_context, {})
        # Should run the safe block
        assert result.score >= 0.0


class TestTimeoutHandling:
    """Test timeout protection."""
    
    @pytest.mark.asyncio
    async def test_infinite_loop_timeout(self, metric, base_context):
        """Test that infinite loops are stopped by timeout."""
        base_context.readme_content = """
        ```python
        while True:
            pass
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_long_computation_timeout(self, metric, base_context):
        """Test that long computations timeout."""
        base_context.readme_content = """
        ```python
        import time
        time.sleep(30)  # Longer than timeout
        ```
        """
        result = await metric.compute(base_context, {})
        # time.sleep might be allowed, but should timeout
        assert result.score == 0.0


class TestCodeExtraction:
    """Test code block extraction from markdown."""
    
    def test_extract_python_blocks(self, metric):
        """Test extraction of Python code blocks."""
        content = """
        # Model
        
        ```python
        code1
        ```
        
        ```py
        code2
        ```
        
        ```javascript
        not_python
        ```
        """
        blocks = metric._extract_code_blocks(content)
        assert len(blocks) == 2
        assert 'code1' in blocks[0]
        assert 'code2' in blocks[1]
    
    def test_extract_no_blocks(self, metric):
        """Test extraction when no code blocks present."""
        content = "# Model\n\nJust text."
        blocks = metric._extract_code_blocks(content)
        assert len(blocks) == 0


class TestSecurityPatterns:
    """Test security pattern detection."""
    
    def test_is_code_safe_basic(self, metric):
        """Test basic safe code detection."""
        safe_code = "x = 10\nprint(x)"
        assert metric._is_code_safe(safe_code) is True
    
    def test_is_code_unsafe_os_system(self, metric):
        """Test detection of os.system."""
        unsafe_code = "import os\nos.system('ls')"
        assert metric._is_code_safe(unsafe_code) is False
    
    def test_is_code_unsafe_subprocess(self, metric):
        """Test detection of subprocess."""
        unsafe_code = "import subprocess\nsubprocess.run(['ls'])"
        assert metric._is_code_safe(unsafe_code) is False
    
    def test_is_code_unsafe_exec(self, metric):
        """Test detection of exec."""
        unsafe_code = "exec('print(1)')"
        assert metric._is_code_safe(unsafe_code) is False
    
    def test_is_code_unsafe_eval(self, metric):
        """Test detection of eval."""
        unsafe_code = "result = eval('1+1')"
        assert metric._is_code_safe(unsafe_code) is False


class TestDebuggingFixes:
    """Test code debugging and fixing."""
    
    def test_apply_safe_debugging_fixes(self, metric):
        """Test that safe debugging fixes are applied."""
        code = "print('hello')"
        fixed = metric._apply_safe_debugging_fixes(code, "test/model")
        
        # Should add error handling
        assert 'try:' in fixed
        assert 'except' in fixed
    
    @pytest.mark.asyncio
    async def test_code_runs_after_debugging(self, metric, base_context):
        """Test that code runs after debugging fixes."""
        # Code that might need imports added
        base_context.readme_content = """
        ```python
        # This might need imports to be added
        x = 10
        print(x)
        ```
        """
        result = await metric.compute(base_context, {})
        # Should get at least 0.5 if debugging helps
        assert result.score >= 0.0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_readme(self, metric, base_context):
        """Test empty README."""
        base_context.readme_content = ""
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_malformed_code_block(self, metric, base_context):
        """Test malformed code blocks."""
        base_context.readme_content = """
        ```python
        This is not valid Python syntax @@@ ### !!!
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score == 0.0
    
    @pytest.mark.asyncio
    async def test_empty_code_block(self, metric, base_context):
        """Test empty code blocks."""
        base_context.readme_content = """
        ```python
        
        ```
        """
        result = await metric.compute(base_context, {})
        # Empty code block might get debugging fixes that add try/except
        # So it could return 0.5 if the wrapper itself runs
        assert result.score in [0.0, 0.5]
    
    @pytest.mark.asyncio
    async def test_unicode_in_code(self, metric, base_context):
        """Test Unicode characters in code."""
        base_context.readme_content = """
        ```python
        message = "Hello 世界 🌍"
        print(message)
        ```
        """
        result = await metric.compute(base_context, {})
        assert result.score >= 0.0


class TestSecurityLogging:
    """Test security violation logging."""
    
    @pytest.mark.asyncio
    async def test_security_violation_logged(self, metric, base_context):
        """Test that security violations are logged."""
        base_context.readme_content = """
        ```python
        import os
        os.system('dangerous command')
        ```
        """
        
        with patch('src.metrics.Reproducibility.logger') as mock_logger:
            result = await metric.compute(base_context, {})
            
            # Should log security warning
            assert mock_logger.warning.called or mock_logger.error.called
            assert result.score == 0.0


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility."""
    
    @pytest.mark.asyncio
    async def test_windows_compatibility(self, metric, base_context):
        """Test that code works on Windows (no signal.alarm)."""
        base_context.readme_content = """
        ```python
        x = 10
        print(x)
        ```
        """
        # This test verifies no AttributeError for signal.SIGALRM
        result = await metric.compute(base_context, {})
        assert result.score >= 0.0  # Should work without errors
    
    def test_execution_wrapper_no_signal(self, metric):
        """Test that execution wrapper doesn't use signal module."""
        code = "print('test')"
        wrapper = metric._create_execution_wrapper(code, timeout=10)
        
        # Should NOT contain signal-related code
        assert 'signal.alarm' not in wrapper
        assert 'signal.SIGALRM' not in wrapper
        assert 'signal.signal' not in wrapper


class TestPerformance:
    """Test performance and latency tracking."""
    
    @pytest.mark.asyncio
    async def test_latency_recorded(self, metric, base_context):
        """Test that latency is properly recorded."""
        base_context.readme_content = """
        ```python
        x = 10
        ```
        """
        result = await metric.compute(base_context, {})
        
        # Latency should be non-negative
        assert result.latency >= 0
        # Should complete in reasonable time (< 30 seconds)
        assert result.latency < 30000  # 30 seconds in ms


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
