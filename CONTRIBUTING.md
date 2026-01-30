# Contributing Guide

Thank you for your interest in contributing to this project!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ecommerce_sales_forecast.git
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Development Setup

### Environment
- Python 3.10+
- PyTorch 2.0+
- CUDA 11.8+ (optional, for GPU)

### Running Tests
```bash
python tests/test_covariate_impact.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings for functions and classes
- Keep functions focused and small

## Pull Request Process

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes
3. Run tests to ensure nothing is broken
4. Commit with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   ```
5. Push and create a Pull Request

### Commit Message Format

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

## Reporting Issues

When reporting issues, please include:
- Python version
- PyTorch version
- Operating system
- Steps to reproduce
- Expected vs actual behavior

## Questions?

Feel free to open an issue for any questions.
