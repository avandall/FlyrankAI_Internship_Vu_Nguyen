from capstone.Multi_platform.core.config import PLATFORM_SPECS

class CaptionGenerator:
    """
    Assembles captions from reusable Prompt Fragments:
    SharedBrandVoice + PlatformRules + ContentSummary
    
    In production: pass fragments to Groq API (e.g. llama-3.3-70b-versatile) for generation.
    Demo: applies rules deterministically to demonstrate the architecture.
    """

    BRAND_VOICE = "FlyRank helps businesses scale their SEO and digital presence. Tone: data-driven, optimistic, actionable."

    PLATFORM_RULES = {
        "instagram": "Max 2200 chars. Start with a hook. Use 5-10 relevant hashtags at end. Include 2-3 emojis. Personal and inspiring tone.",
        "twitter": "Max 280 chars total. One punchy sentence. One key stat or hook. Optional 1-2 hashtags. No filler words.",
        "linkedin": "Max 700 chars. Professional insights. Data or expertise. Call to action at end. No excessive hashtags.",
    }

    def generate(self, platform: str, content: str, title: str) -> str:
        spec = PLATFORM_SPECS.get(platform, {})
        max_chars = spec.get("max_caption_chars", 280)

        summary = content[:200].rstrip() + ("..." if len(content) > 200 else "")

        if platform == "instagram":
            caption = f"✨ {title}\n\n{summary}\n\n💡 Want to grow your online presence? FlyRank's AI-powered tools can help.\n\n#SEO #DigitalMarketing #ContentMarketing #Growth #FlyRank #Marketing"
        elif platform == "twitter":
            hook = title[:80]
            caption = f"🚀 {hook} — Here's what you need to know. #SEO #FlyRank"
            if len(caption) > 280:
                caption = caption[:277] + "..."
        elif platform == "linkedin":
            caption = f"{title}\n\n{summary}\n\nAt FlyRank, we're helping businesses achieve measurable growth. What's your biggest content marketing challenge?"
        else:
            caption = f"{title}: {summary}"

        if len(caption) > max_chars:
            caption = caption[:max_chars - 3] + "..."

        return caption
