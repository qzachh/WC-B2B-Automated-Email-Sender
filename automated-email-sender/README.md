# Automated Email Sender

This tool sends templated HTML emails to contacts listed in a CSV file, with inline images, attachments, and signature support.

## 🔧 Setup Instructions

1. **Clone the Repository** and go into the folder
2. **Install dependencies**:
    ```
    pip install python-dotenv
    ```
3. **Create a `.env` file** based on `.env.example`:
    ```
    SENDER_EMAIL=your-email@example.com
    SENDER_PASSWORD=your-app-password
    ```
4. **Place your assets**:
   - `assets/logo.png`
   - `assets/WeCare_signature.png`
   - `attachments/corporate_solution_teaser.pdf`

5. **Add your contact list** as `data/contacts.csv` with the following headers:
    ```
    name,email,company,gender
    ```

6. **Run the script**:
    ```
    python email_sender.py
    ```

## 🛑 Notes

- Email credentials are read from `.env` for security.
- Do **not** upload `.env` or real contact data to public repositories.
- Daily email limit is configurable in the script.

