from jinja2 import Template

NEWSLETTER_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Daily SCMP News Digest</title>
    <style>
        /* General resets and email client overrides */
        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
        img { -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
        table { border-collapse: collapse !important; }
        body { height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; background-color: #f8fafc; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #334155; }
        
        /* Mobile styles */
        @media screen and (max-width: 600px) {
            .email-container { width: 100% !important; padding-left: 10px !important; padding-right: 10px !important; }
            .card { padding: 20px !important; }
            .header { padding: 20px 20px 10px 20px !important; }
            .spotlight-box { padding: 15px !important; }
            .h1-title { font-size: 20px !important; }
            .h2-title { font-size: 18px !important; }
        }
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <center>
        <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; margin: 0 auto;" class="email-container">
            <!-- Top Utility Bar -->
            <tr>
                <td style="padding: 15px 0 10px 0; text-align: left; font-size: 11px; color: #64748b;" width="100%">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">{{ data.date_header }}</td>
                            <td style="text-align: right;"><a href="#" style="color: #64748b; text-decoration: underline;">Read online</a></td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Main Card Container -->
            <tr>
                <td class="card" style="background-color: #ffffff; border: 1px border #e2e8f0; border-radius: 16px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);" bgcolor="#ffffff">
                    <!-- Header/Brand -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td style="text-align: left; padding-bottom: 25px; border-bottom: 1.5px solid #f1f5f9;">
                                <div style="display: inline-block; font-size: 24px; font-weight: 800; letter-spacing: -0.03em; color: #0f172a;">
                                    SCMP <span style="color: #c2410c;">DAILY DIGEST</span>
                                </div>
                                <div style="font-size: 11px; color: #94a3b8; font-weight: 500; margin-top: 4px; letter-spacing: 0.05em; text-transform: uppercase;">
                                    Your Premium Geopolitics & Tech Briefing
                                </div>
                            </td>
                        </tr>
                    </table>

                    <!-- Greeting & Intro -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px;">
                        <tr>
                            <td style="font-size: 15px; line-height: 1.6; color: #334155;">
                                <p style="margin: 0 0 16px 0; font-weight: 700; font-size: 17px; color: #0f172a;">{{ data.greeting }}</p>
                                <p style="margin: 0 0 20px 0;">Here’s a quick glimpse of what we have curated for you today:</p>
                                
                                <!-- Teaser Bullet Points -->
                                <ul style="margin: 0 0 30px 0; padding-left: 20px; color: #475569;">
                                    {% for teaser in data.teasers %}
                                    <li style="margin-bottom: 8px; font-size: 14.5px;">{{ teaser }}</li>
                                    {% endfor %}
                                </ul>
                            </td>
                        </tr>
                    </table>

                    <!-- SECTION: BREAKING NEWS -->
                    {% if data.breaking_news %}
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 15px; border-top: 1px solid #f1f5f9; padding-top: 25px;">
                        <tr>
                            <td>
                                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #b45309; background-color: #fef3c7; padding: 4px 8px; border-radius: 6px;">Breaking News</span>
                                <h2 class="h2-title" style="font-size: 20px; font-weight: 800; color: #0f172a; margin: 15px 0 10px 0; letter-spacing: -0.02em;">Today's Lead Developments</h2>
                            </td>
                        </tr>
                        {% for item in data.breaking_news %}
                        <tr>
                            <td style="padding-bottom: 25px;">
                                <p style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">
                                    <a href="{{ item.link }}" style="color: #0f172a; text-decoration: none; border-bottom: 1.5px solid #f59e0b;">{{ item.heading }}</a>
                                </p>
                                <p style="margin: 0; font-size: 14.5px; line-height: 1.6; color: #475569;">{{ item.summary }}</p>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}

                    <!-- SECTION: SPOTLIGHT STORY -->
                    {% if data.spotlight_story %}
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 10px; margin-bottom: 30px;">
                        <tr>
                            <td class="spotlight-box" style="background-color: #f8fafc; border: 1.5px solid #e2e8f0; border-radius: 12px; padding: 25px;" bgcolor="#f8fafc">
                                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #0f172a; border-bottom: 2px solid #0f172a; padding-bottom: 2px;">Today's Spotlight</span>
                                <h3 style="font-size: 18px; font-weight: 800; color: #0f172a; margin: 15px 0 12px 0;">
                                    <a href="{{ data.spotlight_story.link }}" style="color: #0f172a; text-decoration: none; border-bottom: 1.5px solid #64748b;">{{ data.spotlight_story.title }}</a>
                                </h3>
                                {% for para in data.spotlight_story.summary_paragraphs %}
                                <p style="margin: 0 0 12px 0; font-size: 14px; line-height: 1.6; color: #334155; {% if loop.last %}margin-bottom: 16px;{% endif %}">{{ para }}</p>
                                {% endfor %}
                                <table border="0" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td>
                                            <a href="{{ data.spotlight_story.link }}" style="background-color: #0f172a; color: #ffffff; text-decoration: none; font-size: 13px; font-weight: 700; padding: 10px 20px; border-radius: 8px; display: inline-block;">Read Full Analysis ➜</a>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    {% endif %}

                    <!-- SECTION: CHINA TECH & AI FRONTIERS -->
                    {% if data.china_tech %}
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 25px;">
                        <tr>
                            <td>
                                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #0369a1; background-color: #e0f2fe; padding: 4px 8px; border-radius: 6px;">Tech & Innovation</span>
                                <h2 class="h2-title" style="font-size: 19px; font-weight: 800; color: #0f172a; margin: 15px 0 15px 0; letter-spacing: -0.02em;">China Tech & AI Frontiers</h2>
                            </td>
                        </tr>
                        {% for item in data.china_tech %}
                        <tr>
                            <td style="padding-bottom: 25px;">
                                <p style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">
                                    <a href="{{ item.link }}" style="color: #0f172a; text-decoration: none; border-bottom: 1.5px solid #0284c7;">{{ item.heading }}</a>
                                </p>
                                <p style="margin: 0; font-size: 14.5px; line-height: 1.6; color: #475569;">{{ item.summary }}</p>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}

                    <!-- SECTION: GEOPOLITICAL DYNAMICS -->
                    {% if data.geopolitics %}
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 25px;">
                        <tr>
                            <td>
                                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #15803d; background-color: #dcfce7; padding: 4px 8px; border-radius: 6px;">Geopolitical Dynamics</span>
                                <h2 class="h2-title" style="font-size: 19px; font-weight: 800; color: #0f172a; margin: 15px 0 15px 0; letter-spacing: -0.02em;">Strategic Regional Angles</h2>
                            </td>
                        </tr>
                        {% for item in data.geopolitics %}
                        <tr>
                            <td style="padding-bottom: 25px;">
                                <p style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700;">
                                    <a href="{{ item.link }}" style="color: #0f172a; text-decoration: none; border-bottom: 1.5px solid #22c55e;">{{ item.heading }}</a>
                                </p>
                                <p style="margin: 0; font-size: 14.5px; line-height: 1.6; color: #475569;">{{ item.summary }}</p>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}

                    <!-- SECTION: QUICK FINDS -->
                    {% if data.quick_finds %}
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 10px; border-top: 1px solid #f1f5f9; padding-top: 25px;">
                        <tr>
                            <td>
                                <span style="font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em; color: #4f46e5; background-color: #e0e7ff; padding: 4px 8px; border-radius: 6px;">Quick Finds</span>
                                <h2 class="h2-title" style="font-size: 19px; font-weight: 800; color: #0f172a; margin: 15px 0 15px 0; letter-spacing: -0.02em;">Additional Insights</h2>
                            </td>
                        </tr>
                        {% for item in data.quick_finds %}
                        <tr>
                            <td style="padding-bottom: 18px;">
                                <p style="margin: 0 0 4px 0; font-size: 15px; font-weight: 700;">
                                    <a href="{{ item.link }}" style="color: #0f172a; text-decoration: none; border-bottom: 1.5px solid #6366f1;">{{ item.heading }}</a>
                                </p>
                                <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #475569;">{{ item.summary }}</p>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}

                    <!-- Footer & Outro -->
                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 30px; border-top: 1.5px solid #f1f5f9; padding-top: 25px;">
                        <tr>
                            <td style="font-size: 14px; line-height: 1.6; color: #64748b;">
                                <p style="margin: 0 0 16px 0;">That is all for today's briefing. We will return tomorrow morning with another comprehensive digest of the shifting global tech and political balance.</p>
                                <p style="margin: 0 0 20px 0; font-style: italic;">Signing off,</p>
                                <p style="margin: 0; font-weight: 800; color: #0f172a;">— SCMP Daily News Agent</p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>

            <!-- Footer Meta -->
            <tr>
                <td style="padding: 30px 0; text-align: center; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                    <p style="margin: 0 0 10px 0;">This email was automatically generated and sent to you by your Antigravity News Assistant.</p>
                    <p style="margin: 0 0 10px 0;">© 2026 SCMP Daily Digest Agent. All rights reserved.</p>
                    <p style="margin: 0;"><a href="#" style="color: #94a3b8; text-decoration: underline;">Update email preferences</a> | <a href="#" style="color: #94a3b8; text-decoration: underline;">Unsubscribe</a></p>
                </td>
            </tr>
        </table>
    </center>
</body>
</html>
"""

def render_newsletter(data):
    """
    Renders the HTML newsletter using the provided dictionary of processed data.
    """
    template = Template(NEWSLETTER_HTML_TEMPLATE)
    return template.render(data=data)
