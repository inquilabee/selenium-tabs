commit:
	git add .
	pre-commit
	git status

pcupdate:
	pre-commit autoupdate
