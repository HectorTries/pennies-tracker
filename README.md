# pennies-tracker

Automated financial content tracker. Scrapes TikTok videos from financial creators, extracts audio, and transcribes for analysis.

## Setup

### GitHub Secrets
Add these secrets to your repo (Settings → Secrets and variables → Actions):

- `OPENAI_API_KEY` - Your OpenAI API key for Whisper transcription

### First Run
1. Go to Actions tab
2. Run the workflow manually
3. Add your OpenAI API key as a secret

## What's It Do?

- Runs daily at 9am UTC (via cron)
- Downloads latest videos from `@pinkpennies_`
- Extracts audio and transcribes via OpenAI Whisper
- Saves everything to `data/videos.json`

## Adding More Creators

Edit `scrape.py` and add more creators to the list. PRs welcome!

## License

MIT
