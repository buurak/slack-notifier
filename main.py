import base64
import os
import json

from slack_sdk.webhook import WebhookClient

STATUS_DICT = {
    "SUCCESS": {"text": "BAŞARILI", "color": "#1EE12C"},
    "FAILURE": {"text": "BAŞARISIZ", "color": "#FF0000"},
    "QUEUED": {"text": "BUILD ALINIYOR", "color": "#FFFB00"},
}
TRIGGER_LIST = [
    "Push-to-backend-test-branch",
    "Push-to-backend-master-branch",
    "Push-to-frontend-test-branch",
    "Push-to-frontend-master-branch",
]
SLACK_WEBHOOK_URL = (
    "https://hooks.slack.com/services/****************************"
)


def build_slack_notifier(event, context):
    build = json.loads(base64.b64decode(event["data"]).decode("utf-8"))

    substitutions = build.get("substitutions")
    status = build.get("status")

    if (substitutions.get("TRIGGER_NAME") not in TRIGGER_LIST) or (
        status not in STATUS_DICT
    ):
        return True

    color = STATUS_DICT[status]["color"]
    status = STATUS_DICT[status]["text"]
    name = "Frontend" if "frontend" in substitutions.get("TRIGGER_NAME") else "Backend"

    attachments = [
        {
            "color": color,
            "blocks": [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"Build - {name}"},
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Branch*\n{substitutions.get('BRANCH_NAME')}",
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status*\n{status}\n<{build['logUrl']}|*View Build Logs*>",
                        },
                    ],
                },
            ],
        }
    ]

    webhook = WebhookClient(SLACK_WEBHOOK_URL)

    try:
        webhook.send(attachments=attachments)
    except Exception as err:
        print(err)

    return True
