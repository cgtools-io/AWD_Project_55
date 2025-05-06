# Agile Web Development Group Project (CITS3403) - CGTools

[ENTER DESCRIPTION HERE]

## Group Members

| **UWA ID** | **Name**   | **GitHub Username** |
|------------|------------|---------------------|
| 23390625      | Cameron Hart    | camhart21  |
| 23214051      | Harry Chan      | Crypteemo  |
| 23245495      | Jordy Kappella  | OgmaLogic  |
| 22957489      | Nick Nasiri     | schain-dev |


## Setup and Installation

1. **Create and activate a virtual environment:**

    ```
    # Create and activate venv
    python3 -m venv venv
    source venv/bin/activate        # Mac/Linux
    .\venv\Scripts\activate         # Windows
    ```

2. **Install dependencies:**

    ```
    pip install -r requirements.txt
    ```

3. **Create your .env file _(optional but recommended)_:**

    ```
    cp .env.example .env
    ```


4. **Run the Flask server:**

    ```
    python run.py
    ```


5. **Access the app:**

    Open your browser and go to:

    ```
    http://localhost:5000
    ```

---

## 🏷️ Issue Label Guide

To help us manage tasks efficiently during the final sprint, we’re using GitHub labels to track priority, status, and task type. Please follow this guide when raising or updating issues.

⚠️ Priority should reflect how urgently the issue affects our assessment criteria (rubric below).

### 🔧 Types of Work
- `logic` – Backend code, data parsing, CGT calculations, database integration
- `styling` – CSS, responsiveness, layout fixes
- `content` – Static content, copywriting, markdown, About page, etc.
- `integration` – Where frontend meets backend (e.g. Flask forms, rendering)
- `refactor` – Code restructuring, cleanup, style reordering
- `bug` – Unexpected or broken behaviour that needs fixing

### 🚦 Priority Levels
- `_priority: high` – Required for submission or **blocking** other tasks
- `_priority: medium` – Valuable but **not blocking**; aim to complete before final review
- `_priority: low` – Nice-to-have or polish; not required for assessment

### ✅ Usage Etiquette
- Only change someone else’s labels after discussion
- If you’re unsure about priority, use `_priority: medium` and add a comment
- Multiple labels are fine (e.g. `styling` + `bug` + `_priority: high`)

---


## ✅ Project Rubric

| Category       | Expectations                                                                                                                                      |
|----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **HTML**       | Valid HTML code, using a wide range of elements, clearly organised with appropriate use of Jinja templates.                                      |
| **CSS**        | Valid, maintainable code, using a wide range of custom selectors and classes. Web page is reactive to screen size.                               |
| **JavaScript** | Valid, well-formatted code, including validation and DOM manipulation/AJAX that uses JavaScript best practices.                                  |
| **Design**     | Good website navigation flow that is intuitive to the user with a strong visual design. The website's purpose is clear and brings value to users.|
| **Content**    | All the features requested in the project brief are implemented appropriately.                                                                    |
| **Flask Code** | Formatted, commented, and well-organised code that responds to requests by performing non-trivial data manipulation and page generation.         |
| **Data Models**| Well-considered database schema, good authentication, and maintainable models. Evidence of database migrations.                                   |
| **Testing**    | Comprehensive test suite with 5+ unit tests and 5+ Selenium tests. Selenium tests should run with a live version of the server.                  |
| **Security**   | Passwords stored as salted hashes. CSRF tokens used to protect forms. Environment variables stored securely in configuration files.              |
| **Commits**    | Regular commits with high-quality messages providing meaningful, concise descriptions and reasoning behind changes.                              |
| **Issues**     | Effective use of GitHub Issues to describe bugs and missing features, including steps to reproduce for bugs.                                     |
| **Pull Requests** | Regular, meaningfully named PRs to add features or fix bugs. Good peer review and issue linkage.                                           |
| **Teamwork**   | Evidence of collaborative workflow on GitHub: code reviews, discussions, and feedback integration.                                                |
