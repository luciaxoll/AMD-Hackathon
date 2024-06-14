import json
from jinja2 import Template

# HTML template for the report
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SARIF Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
    <h1>SARIF Report</h1>
    <h2>Commit:
        <a href="{{ link_url }}">#{{ link_hash }}</a>
    </h2>
    <h2>Tool Information</h2>
    <p><strong>Name:</strong> {{ tool_name }}</p>
    <p><strong>Organization:</strong> {{ organization }}</p>
    <p><strong>Semantic Version:</strong> {{ semantic_version }}</p>

    <h2>Notifications</h2>
    {% for notification in notifications %}
    <table>
        <tr><th>ID</th><td>{{ notification.id }}</td></tr>
        <tr><th>Name</th><td>{{ notification.name }}</td></tr>
        <tr><th>Short Description</th><td>{{ notification.short_description }}</td></tr>
        <tr><th>Full Description</th><td>{{ notification.full_description }}</td></tr>
        <tr><th>Enabled</th><td>{{ notification.enabled }}</td></tr>
        <tr>
            <th>Properties</th>
            <td>
                <ul>
                    {% for key, value in notification.properties.items() %}
                        <li>
                            <strong>{{ key }}:</strong>
                            {% if value is iterable and value is not string %}
                                {{ value | join(', ') }}
                            {% else %}
                                {{ value }}
                            {% endif %}
                        </li>
                    {% endfor %}
                </ul>
            </td>
        </tr>
    </table>
    {% endfor %}

    <h2>Rules</h2>
    {% for rule in rules %}
    <table>
        <tr><th>ID</th><td>{{ rule.id }}</td></tr>
        <tr><th>Name</th><td>{{ rule.name }}</td></tr>
        <tr><th>Short Description</th><td>{{ rule.short_description }}</td></tr>
        <tr><th>Full Description</th><td>{{ rule.full_description }}</td></tr>
        <tr><th>Enabled</th><td>{{ rule.enabled }}</td></tr>
        <tr>
            <th>Properties</th>
            <td>
                <ul>
                    {% for key, value in rule.properties.items() %}
                        <li>
                            <strong>{{ key }}:</strong>
                            {% if value is iterable and value is not string %}
                                {{ value | join(', ') }}
                            {% else %}
                                {{ value }}
                            {% endif %}
                        </li>
                    {% endfor %}
                </ul>
            </td>
        </tr>
    </table>
    {% endfor %}
</body>
</html>
"""

def generate_html_report(sarif_file, output_file, commit_link, commit_hash):
    with open(sarif_file, 'r') as sarif:
        sarif_content = sarif.read()

    data = json.loads(sarif_content)

    tool_info = {}
    notifications = []
    rules = []

    for run in data.get('runs', []):
        tool_info = run.get('tool', {}).get('driver', {})

        for notification in tool_info.get('notifications', []):
            notifications.append({
                'id': notification.get('id'),
                'name': notification.get('name'),
                'short_description': notification.get('shortDescription', {}).get('text'),
                'full_description': notification.get('fullDescription', {}).get('text'),
                'enabled': notification.get('defaultConfiguration', {}).get('enabled'),
                'properties': notification.get('properties')
            })

        for rule in tool_info.get('rules', []):
            rules.append({
                'id': rule.get('id'),
                'name': rule.get('name'),
                'short_description': rule.get('shortDescription', {}).get('text'),
                'full_description': rule.get('fullDescription', {}).get('text'),
                'enabled': rule.get('defaultConfiguration', {}).get('enabled'),
                'properties': rule.get('properties')
            })

    template = Template(html_template)
    html_content = template.render(
        tool_name=tool_info.get('name'),
        organization=tool_info.get('organization'),
        semantic_version=tool_info.get('semanticVersion'),
        notifications=notifications,
        rules=rules,
        link_url=commit_link,
        link_hash = commit_hash
    )

    with open(output_file, 'w') as file:
        file.write(html_content)
    print(f"HTML report generated: {output_file}")

if __name__ == "__main__":
    json_file = 'scans/database-5a7786812dd4-2024-01-11.json'
    output_file = 'sarif_report.html'
    generate_html_report(json_file, output_file)
