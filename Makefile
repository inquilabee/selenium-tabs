commit:
	git add .
	pre-commit
	git status

pcupdate:
	pre-commit autoupdate

publish:
	# Check current version on PyPi
	@echo "Checking current version on PyPI..."
	@poetry show seleniumtabs

	# Update version in pyproject.toml
	@echo "Updating version in pyproject.toml..."
	@poetry version
	@read -p "Enter new version (e.g. 1.0.1): " version; \
	poetry version $$version

	# Run pytest
	@echo "Running tests..."
	@poetry run pytest tests/ -v

	# Commit
	@echo "Committing changes..."
	@git add pyproject.toml
	@git commit -m "Bump version to $$version"
	@git tag -a "v$$version" -m "Version $$version"
	@git push origin main --tags

	# Build and publish
	@echo "Building and publishing package..."
	@poetry build
	@poetry publish

	@echo "Publish complete! Version $$version has been published to PyPI."
