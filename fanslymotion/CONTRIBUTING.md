# Contributing to FanslyMotion

Thank you for your interest in contributing to FanslyMotion! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards others

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template**
3. **Include**:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, GPU, Python version)
   - Error logs/screenshots

### Suggesting Enhancements

1. **Check existing feature requests**
2. **Use the feature request template**
3. **Describe**:
   - Use case and motivation
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m "Add amazing feature"`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/fanslymotion.git
   cd fanslymotion
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   source venv/bin/activate      # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If exists
   ```

4. **Configure environment**:
   ```bash
   copy env.example .env
   # Edit .env with your settings
   ```

5. **Run tests**:
   ```bash
   python test_setup.py
   ```

## Coding Standards

### Python Style Guide

Follow **PEP 8** guidelines:

```python
# Good
def generate_video(image_path: Path, duration: int) -> Path:
    """
    Generate video from image.
    
    Args:
        image_path: Path to input image
        duration: Video duration in seconds
        
    Returns:
        Path to generated video
    """
    # Implementation
    pass

# Bad
def genVideo(img, dur):
    # Implementation
    pass
```

### Code Formatting

Use **black** for code formatting:
```bash
black fanslymotion/
```

### Type Hints

Always use type hints:
```python
from typing import Optional, List
from pathlib import Path

def process_images(paths: List[Path], quality: Optional[int] = None) -> bool:
    pass
```

### Docstrings

Use **Google-style** docstrings:
```python
def complex_function(param1: int, param2: str) -> dict:
    """
    Brief description of function.
    
    Detailed description if needed, explaining the purpose,
    behavior, and any important notes.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Dictionary containing results with keys:
            - 'status': Operation status
            - 'data': Result data
            
    Raises:
        ValueError: If param1 is negative
        IOError: If file cannot be read
        
    Example:
        >>> result = complex_function(42, "test")
        >>> print(result['status'])
        'success'
    """
    pass
```

## Project Structure

```
fanslymotion/
├── bot/              # Telegram bot module
│   ├── bot.py       # Main entry point
│   ├── handlers.py  # Message handlers
│   ├── keyboards.py # Keyboard builders
│   └── states.py    # FSM states
│
├── backend/         # FastAPI backend
│   ├── app.py      # Main application
│   └── models.py   # Pydantic models
│
├── worker/          # RQ worker
│   ├── worker.py   # Worker entry point
│   └── tasks.py    # Job tasks
│
├── svd/            # SVD renderer
│   └── renderer.py # Video generation
│
├── tests/          # Test suite (create this!)
│   ├── test_bot.py
│   ├── test_backend.py
│   ├── test_worker.py
│   └── test_svd.py
│
└── config.py       # Global configuration
```

## Adding New Features

### Example: Adding a New Motion Preset

1. **Update configuration** (`config.py`):
   ```python
   MOTION_PRESETS = {
       # ... existing presets ...
       "shake": {
           "motion_bucket_id": 80,
           "description": "Shake effect"
       }
   }
   ```

2. **Update keyboard** (`bot/keyboards.py`):
   ```python
   motion_labels = {
       # ... existing labels ...
       "shake": "📳 Shake"
   }
   ```

3. **Update renderer** (`svd/renderer.py`):
   ```python
   motion_configs = {
       # ... existing configs ...
       "shake": {
           "motion_bucket_id": 80,
           "noise_aug_strength": 0.2,
       }
   }
   ```

4. **Test the feature**:
   - Test locally
   - Verify different resolutions
   - Check error handling

5. **Update documentation**:
   - Add to README.md
   - Update ARCHITECTURE.md if needed
   - Add examples

### Example: Adding a New API Endpoint

1. **Create Pydantic model** (`backend/models.py`):
   ```python
   class CustomRequest(BaseModel):
       param1: str
       param2: int
   ```

2. **Add endpoint** (`backend/app.py`):
   ```python
   @app.post("/custom/endpoint")
   async def custom_endpoint(request: CustomRequest):
       # Implementation
       return {"status": "ok"}
   ```

3. **Update bot handler** (`bot/handlers.py`):
   ```python
   async def handle_custom_action(message: Message):
       response = await http_client.post(
           f"{settings.backend_url}/custom/endpoint",
           json={"param1": "value", "param2": 42}
       )
   ```

4. **Add tests**
5. **Update API documentation**

## Testing Guidelines

### Unit Tests

```python
# tests/test_svd.py
import pytest
from svd.renderer import SVDRenderer

def test_preprocess_image():
    renderer = SVDRenderer()
    image = renderer.preprocess_image(
        Path("test_image.png"),
        (1280, 720)
    )
    assert image.size == (1280, 720)
```

### Integration Tests

```python
# tests/test_backend.py
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_create_job():
    response = client.post("/job/create", json={
        "user_id": 123,
        "image_data": "base64...",
        "duration": 6,
        "resolution": "720p",
        "motion_preset": "pan_l"
    })
    assert response.status_code == 201
    assert "job_id" in response.json()
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_svd.py

# Run with coverage
pytest --cov=fanslymotion
```

## Documentation

### Inline Comments

```python
# Good: Explain WHY, not WHAT
# Use half precision to reduce VRAM usage by 50%
self.pipeline = StableVideoDiffusionPipeline.from_pretrained(
    model_id,
    torch_dtype=torch.float16
)

# Bad: Explain obvious WHAT
# Set torch_dtype to float16
self.pipeline = StableVideoDiffusionPipeline.from_pretrained(...)
```

### README Updates

When adding features, update:
- Features list
- Usage examples
- Configuration options
- Troubleshooting section

### Architecture Documentation

For significant changes, update `ARCHITECTURE.md`:
- System diagrams
- Data flow
- New components
- Design decisions

## Git Workflow

### Commit Messages

Follow conventional commits:

```
feat: add shake motion preset
fix: resolve GPU memory leak in worker
docs: update README with new motion options
refactor: simplify image preprocessing logic
test: add unit tests for renderer
chore: update dependencies
```

### Branch Naming

```
feature/motion-preset-shake
bugfix/gpu-memory-leak
hotfix/critical-crash
docs/architecture-update
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added unit tests
- [ ] Updated integration tests

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Tests pass
```

## Performance Considerations

### GPU Memory

```python
# Good: Clean up after use
def process_batch(images):
    results = model(images)
    # Process results
    del results
    torch.cuda.empty_cache()
    return processed

# Bad: Memory leak
def process_batch(images):
    results = model(images)
    return results  # Results tensor kept in memory
```

### Async Operations

```python
# Good: Concurrent operations
async def process_multiple(jobs):
    tasks = [process_job(job) for job in jobs]
    return await asyncio.gather(*tasks)

# Bad: Sequential operations
async def process_multiple(jobs):
    results = []
    for job in jobs:
        results.append(await process_job(job))
    return results
```

## Security Best Practices

1. **Never log sensitive data**:
   ```python
   # Good
   logger.info(f"Processing job {job_id}")
   
   # Bad
   logger.info(f"Bot token: {bot_token}")
   ```

2. **Validate all inputs**:
   ```python
   # Good
   if duration not in VideoConfig.DURATIONS:
       raise ValueError(f"Invalid duration: {duration}")
   ```

3. **Sanitize file paths**:
   ```python
   # Good
   from pathlib import Path
   safe_path = Path(base_dir) / Path(user_input).name
   ```

## Release Process

1. **Update version** in `__init__.py`
2. **Update CHANGELOG.md**
3. **Create git tag**: `git tag v1.0.0`
4. **Push tag**: `git push --tags`
5. **Create GitHub release**
6. **Update documentation**

## Getting Help

- **Discord**: [Your Discord]
- **GitHub Discussions**: For questions
- **GitHub Issues**: For bugs/features
- **Email**: [Your email]

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in documentation

---

**Thank you for contributing to FanslyMotion! 🎉**

