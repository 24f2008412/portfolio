import base64
import csv
import io
from bs4 import BeautifulSoup

def generate_app(task: str, brief: str, attachments: list[dict], existing_files: dict = None):
    """
    Generates or updates the application files based on the task, brief, and attachments.
    """
    if "sum-of-sales" in task:
        return generate_sum_of_sales_app(task, brief, attachments, existing_files)
    elif "markdown-to-html" in task:
        return generate_markdown_to_html_app(task, brief, attachments, existing_files)
    elif "github-user-created" in task:
        return generate_github_user_created_app(task, brief, attachments, existing_files)
    else:
        raise ValueError(f"Unknown task: {task}")


def generate_markdown_to_html_app(task: str, brief: str, attachments: list[dict], existing_files: dict = None):
    """
    Handles the 'markdown-to-html' task.
    """
    files = {}

    if not existing_files:
        # Round 1
        markdown_attachment = next((att for att in attachments if att["name"] == "input.md"), None)
        if not markdown_attachment:
            raise ValueError("input.md attachment not found")

        # Decode the base64 content
        md_data_uri = markdown_attachment["url"]
        header, encoded = md_data_uri.split(",", 1)
        decoded_md = base64.b64decode(encoded).decode("utf-8")
        files["input.md"] = decoded_md

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown to HTML</title>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/default.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
</head>
<body>
    <div id="markdown-output"></div>
    <script>
        document.addEventListener('DOMContentLoaded', (event) => {{
            fetch('input.md')
                .then(response => response.text())
                .then(text => {{
                    document.getElementById('markdown-output').innerHTML = marked.parse(text);
                    hljs.highlightAll();
                }});
        }});
    </script>
</body>
</html>
"""
        files["index.html"] = html_content
    else:
        # Round 2
        if "Add tabs" in brief:
            soup = BeautifulSoup(existing_files["index.html"], "html.parser")

            # Create tabs
            tabs_container = soup.new_tag("div", **{ "class": "tabs-container" })

            html_button = soup.new_tag("button", **{"id": "html-tab-button", "class": "tab-button active"})
            html_button.string = "HTML"

            markdown_button = soup.new_tag("button", **{"id": "markdown-tab-button", "class": "tab-button"})
            markdown_button.string = "Markdown"

            tabs_container.append(html_button)
            tabs_container.append(markdown_button)

            # Create markdown source container
            markdown_source_container = soup.new_tag("pre", **{"id": "markdown-source", "style": "display: none;"})

            # Add elements to body
            body = soup.find("body")
            body.insert(0, tabs_container)
            body.append(markdown_source_container)

            # Update script
            script_tag = soup.find("script", {"src": None}) # Find inline script
            script_tag.string = """
document.addEventListener('DOMContentLoaded', (event) => {
    const htmlOutput = document.getElementById('markdown-output');
    const markdownSource = document.getElementById('markdown-source');
    const htmlTabButton = document.getElementById('html-tab-button');
    const markdownTabButton = document.getElementById('markdown-tab-button');

    let markdownContent = '';

    fetch('input.md')
        .then(response => response.text())
        .then(text => {
            markdownContent = text;
            htmlOutput.innerHTML = marked.parse(markdownContent);
            markdownSource.textContent = markdownContent;
            hljs.highlightAll();
        });

    htmlTabButton.addEventListener('click', () => {
        htmlOutput.style.display = 'block';
        markdownSource.style.display = 'none';
        htmlTabButton.classList.add('active');
        markdownTabButton.classList.remove('active');
    });

    markdownTabButton.addEventListener('click', () => {
        htmlOutput.style.display = 'none';
        markdownSource.style.display = 'block';
        htmlTabButton.classList.remove('active');
        markdownTabButton.classList.add('active');
    });
});
"""

            files["index.html"] = str(soup)

    return files


def generate_github_user_created_app(task: str, brief: str, attachments: list[dict], existing_files: dict = None):
    """
    Handles the 'github-user-created' task.
    """
    files = {}
    seed = task.split('-')[-1]

    if not existing_files:
        # Round 1
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub User Account Creation Date</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>GitHub User Account Creation Date</h1>
        <form id="github-user-{seed}">
            <div class="mb-3">
                <label for="username" class="form-label">GitHub Username</label>
                <input type="text" class="form-control" id="username" required>
            </div>
            <div class="mb-3">
                <label for="token" class="form-label">Optional GitHub Token</label>
                <input type="text" class="form-control" id="token">
            </div>
            <button type="submit" class="btn btn-primary">Get Creation Date</button>
        </form>
        <div id="github-created-at" class="mt-3"></div>
    </div>
    <script>
        document.getElementById('github-user-{seed}').addEventListener('submit', function(event) {{
            event.preventDefault();
            const username = document.getElementById('username').value;
            const token = document.getElementById('token').value;
            const headers = {{
                'Accept': 'application/vnd.github.v3+json'
            }};
            if (token) {{
                headers['Authorization'] = `token ${{token}}`;
            }}

            fetch(`https://api.github.com/users/${{username}}`, {{ headers }})
                .then(response => response.json())
                .then(data => {{
                    if (data.created_at) {{
                        const date = new Date(data.created_at);
                        const year = date.getUTCFullYear();
                        const month = String(date.getUTCMonth() + 1).padStart(2, '0');
                        const day = String(date.getUTCDate()).padStart(2, '0');
                        document.getElementById('github-created-at').textContent = `${{year}}-${{month}}-${{day}}`;
                    }} else {{
                        document.getElementById('github-created-at').textContent = 'User not found or error fetching data.';
                    }}
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    document.getElementById('github-created-at').textContent = 'An error occurred.';
                }});
        }});
    </script>
</body>
</html>
"""
        files["index.html"] = html_content
    else:
        # Round 2
        if "Show an aria-live alert" in brief:
            soup = BeautifulSoup(existing_files["index.html"], "html.parser")

            # Add status alert
            status_alert = soup.new_tag("div", **{"id": "github-status", "class": "alert", "aria-live": "polite"})
            form = soup.find("form")
            form.insert_after(status_alert)

            # Update script
            script_tag = soup.find("script")
            script_tag.string = f"""
document.getElementById('github-user-{seed}').addEventListener('submit', function(event) {{
    event.preventDefault();
    const username = document.getElementById('username').value;
    const token = document.getElementById('token').value;
    const statusDiv = document.getElementById('github-status');
    const resultDiv = document.getElementById('github-created-at');

    statusDiv.textContent = 'Looking up user...';
    statusDiv.className = 'alert alert-info';

    const headers = {{
        'Accept': 'application/vnd.github.v3+json'
    }};
    if (token) {{
        headers['Authorization'] = `token ${{token}}`;
    }}

    fetch(`https://api.github.com/users/${{username}}`, {{ headers }})
        .then(response => {{
            if (!response.ok) {{
                throw new Error('Network response was not ok');
            }}
            return response.json();
        }})
        .then(data => {{
            if (data.created_at) {{
                const date = new Date(data.created_at);
                const year = date.getUTCFullYear();
                const month = String(date.getUTCMonth() + 1).padStart(2, '0');
                const day = String(date.getUTCDate()).padStart(2, '0');
                resultDiv.textContent = `${{year}}-${{month}}-${{day}}`;
                statusDiv.textContent = 'Success!';
                statusDiv.className = 'alert alert-success';
            }} else {{
                resultDiv.textContent = '';
                statusDiv.textContent = 'User not found.';
                statusDiv.className = 'alert alert-danger';
            }}
        }})
        .catch(error => {{
            console.error('Error:', error);
            resultDiv.textContent = '';
            statusDiv.textContent = 'An error occurred.';
            statusDiv.className = 'alert alert-danger';
        }});
}});
"""
            files["index.html"] = str(soup)

    return files


def generate_sum_of_sales_app(task:str, brief: str, attachments: list[dict], existing_files: dict = None):
    """
    Handles the 'sum-of-sales' task.
    """
    files = {}

    # Round 1: Generate initial files
    if not existing_files:
        # Find the data.csv attachment
        data_csv_attachment = next((att for att in attachments if att["name"] == "data.csv"), None)
        if not data_csv_attachment:
            raise ValueError("data.csv attachment not found")

        # Decode the base64 content
        csv_data_uri = data_csv_attachment["url"]
        header, encoded = csv_data_uri.split(",", 1)
        decoded_csv = base64.b64decode(encoded).decode("utf-8")
        files["data.csv"] = decoded_csv

        # Calculate the total sales
        total_sales = 0
        reader = csv.DictReader(io.StringIO(decoded_csv))
        for row in reader:
            total_sales += float(row["sales"])

        # Extract seed from task
        seed = task.split('-')[-1]

        # Generate the HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sales Summary {seed}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>Sales Summary</h1>
        <div id="total-sales">{total_sales:.2f}</div>
    </div>
</body>
</html>
"""
        files["index.html"] = html_content
    # Round 2: Update existing files
    else:
        if "Add a Bootstrap table" in brief:
            # Get existing data.csv
            csv_content = existing_files.get("data.csv")
            if not csv_content:
                raise ValueError("data.csv not found in existing files for Round 2")

            # Calculate product sales
            product_sales = {}
            total_sales = 0
            reader = csv.DictReader(io.StringIO(csv_content))
            for row in reader:
                product = row["product"]
                sales = float(row["sales"])
                product_sales[product] = product_sales.get(product, 0) + sales
                total_sales += sales

            # Parse existing HTML
            soup = BeautifulSoup(existing_files["index.html"], "html.parser")

            # Create the product sales table
            table = soup.new_tag("table", **{"class": "table", "id": "product-sales"})
            thead = soup.new_tag("thead")
            tbody = soup.new_tag("tbody")

            # Table header
            tr = soup.new_tag("tr")
            th_product = soup.new_tag("th")
            th_product.string = "Product"
            th_sales = soup.new_tag("th")
            th_sales.string = "Total Sales"
            tr.append(th_product)
            tr.append(th_sales)
            thead.append(tr)
            table.append(thead)

            # Table body
            for product, sales in product_sales.items():
                tr = soup.new_tag("tr")
                td_product = soup.new_tag("td")
                td_product.string = product
                td_sales = soup.new_tag("td")
                td_sales.string = f"{sales:.2f}"
                tr.append(td_product)
                tr.append(td_sales)
                tbody.append(tr)
            table.append(tbody)

            # Find the container and add the table
            container = soup.find("div", {"class": "container"})
            if container:
                container.append(table)

            # Update total sales
            total_sales_div = soup.find("div", {"id": "total-sales"})
            if total_sales_div:
                total_sales_div.string = f"{total_sales:.2f}"

            files["index.html"] = str(soup)

    return files