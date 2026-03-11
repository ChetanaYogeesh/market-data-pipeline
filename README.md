## Data Pipeline Codebase Architecture: Python Project Structure Guide

This project demonstrates how to build a modern data pipeline in Python, with a clean project structure, reproducible environments, and AI-assisted development using Cursor.

---

## Vibe Coding Setup Checklist: Essential Tools for AI Data Pipeline Projects

Before starting to build your AI-powered data pipeline, you'll need to set up accounts for four essential services. Each provides free tiers that are perfect for learning and development.

### GitHub account

GitHub will host your code repository and integrate with Streamlit for deployment. It's essential for version control and collaboration.

**Setup steps:**

1. Visit `https://github.com` and create a free account.
2. Verify your email address.

### Streamlit account

It’s easy to use Streamlit to build and deploy data visualization dashboards with Python. Streamlit’s free tier includes cloud hosting.

**Setup steps:**

1. Go to `https://streamlit.io` and sign up with your GitHub account; this automatically links your repositories for easy deployment.
2. Verify your email address.
3. Explore the dashboard to familiarize yourself with the interface.
4. No API keys are needed; GitHub integration handles authentication.

### Cursor IDE setup

Cursor is an AI-powered code editor that can dramatically speed up your development process. It provides intelligent code completion and AI assistance.

**Setup steps:**

1. Download Cursor from `https://cursor.sh`.
2. Install the application on your system.
3. Sign up for a free account when prompted.

### Neon database account

Neon provides serverless PostgreSQL databases with a generous free tier that will store and process your pipeline data.

**Setup steps:**

1. Visit `https://neon.tech` and create an account.
2. Create your first database project.
3. Choose your preferred region for optimal performance.

### Verification checklist

Before proceeding, ensure you have:

- **GitHub** account
- **Streamlit** account linked to GitHub
- **Cursor IDE** installed and configured
- **Neon database** created with connection details

### Quick start tips

**Security best practices:**

- **Never commit API keys** to version control.
- **Use environment variables** for sensitive data.
- **Keep a secure backup** of all credentials.

With these tools configured, you're ready to start building your AI-powered data pipeline. The combination of real-time data, intelligent development tools, cloud database, and easy deployment makes this a powerful stack for data engineering projects.

---

## Version control with GitHub

Always maintain a remote repository for your data pipeline project and commit changes regularly. This provides backup, enables collaboration, and creates a history of your development progress.

### Repository setup

- **Create a dedicated repository** for your pipeline project.
- **Initialize with a clear README** explaining your project's purpose.
- **Use descriptive commit messages** that explain what changed and why.
- **Push changes to GitHub** after completing each feature or fix.

### Commit best practices

- **Commit early and often**: don't wait until everything is perfect.
- **Make atomic commits** that represent single logical changes.
- **Write clear commit messages**:  
  - Prefer: `Add data validation for stock prices`  
  - Avoid: `update code`
- **Push to remote at least once per day** to prevent data loss.
- **Use `.gitignore`** to exclude sensitive files like `.env` and API keys.

Regular commits to GitHub not only protect your work but also demonstrate your development progress and coding discipline to potential employers.

---

## Virtual environments

Python virtual environments (venvs) are isolated Python installations that keep your project dependencies separate from your system Python and other projects.

### What they are

Think of a virtual environment as a dedicated workspace for each project. When you activate a venv, Python only sees the packages you've specifically installed in that environment.

### Why you want them

- **Dependency isolation**: different projects often need different versions of the same package—without venvs, installing `pandas 2.0` for one project might break another project that requires `pandas 1.5`.
- **Clean development**: your system Python stays clean, and you can easily see exactly which packages your project actually needs.
- **Reproducible environments**: you can recreate the exact same setup on different machines or share it with teammates using a `requirements.txt` file.
- **Easy cleanup**: if you make a mistake or have finished a project, just delete the `venv` folder and start fresh.

### How to create and activate a virtual environment

```bash
python3 -m venv .venv   # create the virtual environment
source .venv/bin/activate   # activate it
```

### Managing dependencies with `requirements.txt`

A `requirements.txt` file is a simple text document that lists the Python packages your project needs. It's the standard way to manage dependencies in Python development.

When working with virtual environments, you create a `requirements.txt` file listing your essential libraries (like `pandas`, `streamlit`, or `psycopg2`) along with optional version specifications. Then anyone can recreate your project's environment by running:

```bash
pip install -r requirements.txt
```

This automatically downloads and installs not just the packages you specified, but also all their underlying dependencies at compatible versions.

**Example of a `requirements.txt` file:**

```text
pandas==2.0.3
requests==2.31.0
streamlit==1.28.0
psycopg2-binary==2.9.7
```

---

## Working with Cursor

Cursor offers two distinct modes for AI assistance: **Agent mode** and **Ask mode**.

- **Agent mode** is designed for getting things done: it's proactive and will take whatever actions are necessary to complete tasks, including reading files, writing code, running terminal commands, and even searching the web.
- **Ask mode** is purely conversational and designed for understanding your codebase without making changes.

For building projects like data pipelines, **Agent mode** proves invaluable as it can orchestrate complex multistep processes. The agent creates organized to-do lists before starting work and always requests permission before executing potentially impactful terminal commands, giving you control over the process.

### Tips for using Cursor effectively

- **Start fresh conversations** for new tasks using the plus sign to prevent context contamination between different objectives.
- The agent **doesn't retain memory** from previous chats, but it compensates by intelligently exploring your codebase to understand the current state.
- You can **reference specific files using the `@` symbol**, though this isn't always necessary, as the agent can discover relevant files independently.
- The agent **cannot see git-ignored files** like `.env` files containing secrets, but you can inform it about their existence and structure without exposing sensitive information.

Beyond the main chat interface, Cursor's **Tab completion** feature provides real-time code suggestions as you type.

Set up **Cursor Rules** in your project settings to establish consistent behaviors, such as ensuring the agent always activates your virtual environment.

The agent excels at consolidating scattered logic into organized, production-ready code and can handle complex tasks like setting up databases, implementing testing frameworks, and deploying applications.

However, always **verify the agent's work**, as it may create extra files or add test data that needs to be cleaned up. Provide specific feedback when outputs don't meet your expectations. The agent responds well to iterative refinement and can adapt its approach based on your guidance.

---

## Pipeline architecture

The data pipeline built in this project demonstrates a robust, production-ready architecture that follows modern data engineering principles.

### Layers of the pipeline

- **Data extraction** using the OpenAlex API through the `pyalex` library.
- **Data storage** in a cloud-hosted Neon PostgreSQL database.
- **Data visualization** through a Streamlit dashboard.

This separation of concerns allows each component to be developed, tested, and maintained independently while working together seamlessly.

### Data quality and reliability

The architecture prioritizes data quality and reliability through multiple safeguards:

- **Deduplication logic** ensures no duplicate papers enter the database.
- **Comprehensive data quality tests** validate data integrity across multiple dimensions, including completeness, uniqueness, and consistency.
- The pipeline **handles API pagination automatically** to ensure complete data extraction, and implements proper **error handling and logging** throughout the process.
- All sensitive information like database credentials is **managed through environment variables** and kept separate from the codebase using `.env` files and git-ignore-style patterns.

### Execution and visualization

- The final pipeline consolidates all logic into a **single executable script** that can be run from the command line with configurable parameters, making it suitable for automated scheduling or manual execution.
- The accompanying **Streamlit dashboard** connects directly to the database for real-time data visualization and can be deployed to the web for public access.

This end-to-end solution demonstrates how AI-assisted development can rapidly create sophisticated data infrastructure that would traditionally require extensive manual coding and configuration.
