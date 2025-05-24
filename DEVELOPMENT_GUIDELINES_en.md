# CATalogue Project Development Guidelines

## 1. Project Structure
- Standard Flask project structure
- Core code in app/ directory
- Tests in tests/ directory
- Static resources in static/ directory
- Templates in templates/ directory

## 2. Naming Conventions
### File Naming
- Python files: lowercase_with_underscores (e.g. cat_service.py)
- Template files: lowercase_with_underscores (e.g. edit_cat.html)
- Test files: test_prefix + tested_filename (e.g. test_cat_service.py)

### Port Naming
- Main service port: 5000
- Test port: 5001
- Configure via environment variable: `APP_PORT`

### Variable Naming
- Python variables: lowercase_with_underscores (e.g. cat_list)
- Class names: PascalCase (e.g. CatService)
- Constants: UPPERCASE_WITH_UNDERSCORES (e.g. MAX_UPLOAD_SIZE)

## 3. Code Quality Requirements
- Portability: Use environment variables for paths and parameters
- Code reuse:
  - Common functions in app/core/
  - Services inherit from BaseService
  - Routes use BaseCRUD
- Extensibility:
  - Plugin-based design
  - Organize routes with Blueprints

## 4. Documentation Standards
- Provide both Chinese and English documentation
- Master document: [README.md](README.md)
- English comments for public interfaces and templates
- Chinese comments for other code

## 5. Testing Standards
- Each Python module should have corresponding test file
- Test coverage >80%
- Use pytest framework
- Test data in tests/fixtures/ directory

## 6. Pre-commit Checklist
1. Is documentation updated?
2. Are tests added?
3. Does it follow naming conventions?
4. Is portability considered?
5. Is code reuse reasonable?
6. Are extension points clear?

## 7. Future Development Suggestions
- Add API documentation (Swagger)
- Implement CI/CD pipeline
- Add Docker support
- Add performance tests
- Improve monitoring system
