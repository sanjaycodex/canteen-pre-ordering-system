# Git steps for the Canteen Pre-Ordering System

Run these yourself, one block at a time. Your commit history is part of the marks, and you must be able to explain each command. Use **Git Bash** on Windows (it understands `cp` and `mkdir`). Replace `[Your Name]`, `[Register Number]` and `[your-username]` in README.md before the last commit.

Folder layout in this zip:
- `full-project/`  : the finished project (copy files FROM here)
- `stages/`        : two early versions of files used in the first commits

You will work in a NEW folder next to these. Below, `FP` means the path to `full-project` (e.g. `../full-project`).

## 0. One-time setup
```bash
git config --global user.name "Your Name"
git config --global user.email "your-github-email@example.com"
mkdir canteen-pre-ordering-system
cd canteen-pre-ordering-system
git init -b main
```
Create an empty repo on github.com named `canteen-pre-ordering-system` (Public, no README, no .gitignore).

## 1. Initial commit (main)
```bash
mkdir cps tests
cp FP/.gitignore .
cp FP/cps/__init__.py cps/
cp FP/tests/__init__.py tests/
cp STAGES/README_skeleton.md README.md
git add -A
git commit -m "Initial commit: project structure, .gitignore and README skeleton"
git remote add origin https://github.com/[your-username]/canteen-pre-ordering-system.git
```

## 2. Schema and validators (main)
```bash
cp FP/cps/database.py FP/cps/validators.py cps/
git add -A
git commit -m "Add SQLite schema and input validators"
```

## 3. Feature branch: menu management
```bash
git checkout -b feature/menu-management
cp FP/cps/menu.py cps/
git add -A
git commit -m "Add menu management module (add, list, search, update stock, remove)"
git checkout main
git merge --no-ff feature/menu-management -m "Merge branch 'feature/menu-management' into main"
```

## 4. Feature branch: student registration
```bash
git checkout -b feature/student-registration
cp FP/cps/students.py cps/
git add -A
git commit -m "Add student registration and lookup module"
git checkout main
git merge --no-ff feature/student-registration -m "Merge branch 'feature/student-registration' into main"
```

## 5. Feature branch: order placement (first half of orders.py)
```bash
git checkout -b feature/order-placement
cp STAGES/orders_part1.py cps/orders.py
git add -A
git commit -m "Add order placement with stock update, token and total bill; cancellation"
git checkout main
git merge --no-ff feature/order-placement -m "Merge branch 'feature/order-placement' into main"
```

## 6. Feature branch: order status tracking (final orders.py)
```bash
git checkout -b feature/order-status
cp FP/cps/orders.py cps/orders.py
git add -A
git commit -m "Add order status tracking and pending orders list"
git checkout main
git merge --no-ff feature/order-status -m "Merge branch 'feature/order-status' into main"
```

## 7. Feature branch: CLI menu
```bash
git checkout -b feature/cli-menu
cp FP/main.py .
git add -A
git commit -m "Add interactive CLI menu with error handling"
git checkout main
git merge --no-ff feature/cli-menu -m "Merge branch 'feature/cli-menu' into main"
```
Run `python main.py` now and test it. This is where you take Figures 1 and 2.

## 8. Feature branch: testing
```bash
git checkout -b feature/testing
cp FP/tests/test_cps.py tests/
python -m unittest -v          # must show 20 tests, OK (take Figure 3)
git add -A
git commit -m "Add unit tests for validators, menu, students and orders (20 tests)"
git checkout main
git merge --no-ff feature/testing -m "Merge branch 'feature/testing' into main"
```

## 9. Docs branch: README
Copy the final README, then edit your name, register number, subject and GitHub username inside it.
```bash
git checkout -b docs/readme
cp FP/README.md .
# edit README.md now: replace every [placeholder]
git add -A
git commit -m "Complete README with all required sections"
git checkout main
git merge --no-ff docs/readme -m "Merge branch 'docs/readme' into main"
```
That makes 16 commits (2 on main + 7 branches x commit and merge) and 7 branches, as the report says.

## 10. Push to GitHub
```bash
git push -u origin --all
```
If asked to log in, use your GitHub account (browser sign-in or a personal access token). Confirm that the repo is **Public** (Settings, General).

## 11. Evidence screenshots
| Figure | Command / page |
|---|---|
| 1, 2 | `python main.py` (add items and a student, one invalid phone/price, place an order) |
| 3 | `python -m unittest -v` |
| 4 | `git log --pretty=format:"%h %ad %s" --date=format:"%Y-%m-%d %H:%M"` |
| 5 | `git log --graph --pretty=format:"%h %s"` |
| 6 | `git branch`, `git log --merges --oneline`, `git ls-files` |
| 7 | GitHub repository main page |
| 8 | GitHub, Commits page of main |

## 12. Finish
1. Open the repo URL in an incognito window to confirm it loads.
2. Paste your screenshots into the PDF boxes (or tell me and I will insert them for you), fill in the name, register number, course and URL.
3. Save the PDF as `<RegisterNumber>_Assignment2_MiniProject.pdf`.
4. Submit the PDF and the repo URL on the course portal before the deadline.

## If something goes wrong
- Wrong commit message on the LAST commit: `git commit --amend -m "new message"` (before pushing).
- Forgot a file in the last commit: `git add file && git commit --amend --no-edit`.
- Push rejected because the GitHub repo is not empty: create a fresh empty repo, do not add a README there.
