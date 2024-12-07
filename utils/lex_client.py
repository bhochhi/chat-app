import boto3

class LexClient:
    def __init__(self, config):
        self.client = boto3.client(
            'lexv2-runtime',
            region_name=config.AWS_REGION
        )
        self.bot_id = config.BOT_ID
        self.bot_alias_id = config.BOT_ALIAS_ID
        self.locale_id = config.LOCALE_ID

    def send_message(self, message):
        try:
            response = self.client.recognize_text(
                botId=self.bot_id,
                botAliasId=self.bot_alias_id,
                localeId=self.locale_id,
                sessionId='test-session',
                text=message
            )
            return response
        except Exception as e:
            return {"error": str(e)}
