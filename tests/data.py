"""Tests for the v1/data endpoint"""

import requests

def test_email(email: str):
    response = requests.post('http://localhost:5000/v1/data', json={'email': email}).json()

    if response['status'] == 200:
        print(response['response'])
    else:
        raise Exception(response['response'])

if __name__ == '__main__':
    emails = [
        """
        Subject: Upcoming Company-Wide Town Hall & Important Announcements

        Dear Team,

        We hope this email finds you well. As we gear up for the second quarter, we have several important updates and events to share with you. Please take a moment to review the information below:

        1. Company-Wide Town Hall:

        Date: June 15, 2024
        Time: 10:00 AM - 12:00 PM (PST)
        Location: Main Auditorium (Building A) / Zoom (Link to be provided)
        Agenda:
        CEO's Vision for the Upcoming Year
        Departmental Achievements and Goals
        Q&A Session with Leadership
        2. New Health and Wellness Programs:

        Mental Health Support: Access to 24/7 counseling services through our new partnership with MindWell.
        Fitness Subsidies: Up to $500 annually for gym memberships, fitness classes, or home workout equipment.
        Nutrition Workshops: Monthly virtual sessions on healthy eating habits and meal planning.
        3. Software Development Best Practices Workshop:

        Date: June 25, 2024
        Time: 2:00 PM - 4:00 PM (PST)
        Facilitator: John Doe, Senior Software Engineer
        Topics: Code Review Techniques, Testing Strategies, and CI/CD Integration
        RSVP: Please confirm your attendance by June 20, 2024.
        4. Upcoming Release Schedule:

        Version 3.2: Beta release on July 1, 2024, and full release on August 15, 2024.
        New Features: Enhanced security protocols, updated user interface, and improved performance metrics.
        5. Employee Recognition Program:

        Nominations Open: Submit your nominations for outstanding team members who have gone above and beyond in their roles.
        Deadline: June 30, 2024
        Award Ceremony: During the Town Hall on June 15, 2024.
        We appreciate your continued dedication and hard work. Please mark these dates on your calendar and stay tuned for further updates.

        Best regards,

        John Morris
        HR Department
        Big Bang Inc.
        johnmorris@bigbang.com
        """,
        """
        Subject: Introduction and Team Collaboration

        Hi Jim,

        I hope this email finds you well. My name is Alex Johnson, and I'm a software developer at [Big Tech Company]. I recently joined the team and wanted to take a moment to introduce myself and connect with you.

        I've been working in software development for over six years, primarily focusing on backend development and cloud infrastructure. In my previous role, I led a team that successfully migrated a large-scale application to a microservices architecture, improving scalability and performance. I’m passionate about coding best practices, automation, and DevOps.

        I look forward to collaborating with you on our upcoming projects. Please let me know if there's anything specific you need from me or if you'd like to discuss any particular aspects of our work.

        Best regards,
        Alex Johnson
        alex.johnson@[bigtechcompany].com
        """,
        """
        Subject: Upcoming Project Deadline and Personal Update

        Hi Bob,

        I hope this email finds you well. I wanted to remind you about the upcoming project deadline on June 15th. We're making good progress, but there are a few critical tasks that need to be completed by next week. I've outlined these tasks in our project management tool, and I would appreciate it if you could take a look and update your status accordingly.

        On a personal note, I wanted to let you know that I will be taking a few days off from May 25th to May 28th. My wife and I are expecting our first child, and I want to be there for the birth and help her during the initial days. I'll be available for any urgent matters via email, but I hope you can understand if my response times are a bit slower during that period.

        Thank you for your understanding and cooperation. Let's keep pushing forward to ensure we meet our deadline with a high-quality deliverable.

        Best regards,

        John

        Software Developer at Big Tech Co.
        john@big.co
        767-555-1234
        """
    ]

    for email in emails:
        test_email(email)
        print()