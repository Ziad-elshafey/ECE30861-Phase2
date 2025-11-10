"""Quick test to verify URL parsing logic."""

def parse_artifact_name(url: str) -> tuple[str, str]:
    """
    Parse artifact names from URL.
    
    Returns:
        (full_name, artifact_name) tuple
        - full_name: used for validation (e.g., "owner/repo")
        - artifact_name: stored in DB (e.g., "repo")
    """
    url_parts = url.strip("/").split("/")
    
    # Extract full model identifier for validation (e.g., "owner/repo")
    if len(url_parts) >= 2:
        full_model_name = "/".join(url_parts[-2:])
    else:
        full_model_name = url_parts[-1]
    
    # Remove .git suffix if present (for GitHub URLs)
    if full_model_name.endswith('.git'):
        full_model_name = full_model_name[:-4]
    
    # For storage: Extract just the artifact name (WITHOUT owner prefix)
    artifact_name = url_parts[-1]
    if artifact_name.endswith('.git'):
        artifact_name = artifact_name[:-4]
    
    return full_model_name, artifact_name


# Test cases
test_urls = [
    "https://huggingface.co/google-bert/bert-base-uncased",
    "https://github.com/owner/repo",
    "https://github.com/owner/repo.git",
    "https://huggingface.co/datasets/bookcorpus",
]

print("URL Parsing Test")
print("=" * 80)
for url in test_urls:
    full, artifact = parse_artifact_name(url)
    print(f"\nURL: {url}")
    print(f"  Full name (for validation):  {full}")
    print(f"  Artifact name (for storage): {artifact}")

print("\n" + "=" * 80)
print("Expected behavior:")
print("- Full name should be 'owner/repo' for validation")
print("- Artifact name should be just 'repo' for storage (per OpenAPI spec)")
