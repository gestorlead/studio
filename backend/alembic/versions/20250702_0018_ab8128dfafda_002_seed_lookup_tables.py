"""002_seed_lookup_tables - Populate lookup tables with initial data

Revision ID: ab8128dfafda
Revises: db4acd9fe490
Create Date: 2025-07-02 00:18:17.123456

This migration populates all lookup tables with initial seed data:
- Subscription tiers (Free, Pro, Enterprise)
- AI providers (OpenAI, Anthropic, Google, etc.)
- Task types (text generation, image generation, etc.)
- Provider models with capabilities
- Agent categories and types
- Campaign types

Based on market research and common use cases.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'ab8128dfafda'
down_revision: Union[str, Sequence[str], None] = 'db4acd9fe490'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Populate lookup tables with seed data."""
    
    # 1. SUBSCRIPTION TIERS
    op.execute(text("""
        INSERT INTO subscription_tiers (tier_name, monthly_credits, max_agents, monthly_price_cents) VALUES
        ('free', 100, 2, 0),
        ('pro', 1000, 10, 2900),
        ('enterprise', 5000, 50, 9900),
        ('unlimited', -1, -1, 29900);
    """))
    
    # 2. AI PROVIDERS
    op.execute(text("""
        INSERT INTO ai_providers (provider_name, display_name, api_base_url, is_active) VALUES
        ('openai', 'OpenAI', 'https://api.openai.com/v1', true),
        ('anthropic', 'Anthropic', 'https://api.anthropic.com', true),
        ('google', 'Google Gemini', 'https://generativelanguage.googleapis.com/v1', true),
        ('mistral', 'Mistral AI', 'https://api.mistral.ai/v1', true),
        ('huggingface', 'Hugging Face', 'https://api-inference.huggingface.co', true),
        ('replicate', 'Replicate', 'https://api.replicate.com/v1', true),
        ('stability', 'Stability AI', 'https://api.stability.ai', true),
        ('elevenlabs', 'ElevenLabs', 'https://api.elevenlabs.io/v1', true);
    """))
    
    # 3. TASK TYPES
    op.execute(text("""
        INSERT INTO task_types (type_name, description, category, default_credit_cost) VALUES
        -- Text Generation
        ('text_generation', 'Generate text content using AI models', 'content', 1),
        ('copywriting', 'Marketing copy and sales content', 'marketing', 2),
        ('blog_writing', 'Blog posts and articles', 'content', 3),
        ('social_media', 'Social media posts and captions', 'marketing', 1),
        ('email_writing', 'Email campaigns and newsletters', 'marketing', 2),
        ('translation', 'Text translation between languages', 'content', 1),
        ('summarization', 'Text summarization and extraction', 'content', 1),
        ('code_generation', 'Programming code generation', 'development', 2),
        
        -- Image Generation
        ('image_generation', 'AI-generated images and artwork', 'visual', 5),
        ('image_editing', 'Image manipulation and enhancement', 'visual', 3),
        ('logo_design', 'Logo and brand identity creation', 'design', 8),
        ('product_images', 'Product photography and mockups', 'marketing', 6),
        ('social_graphics', 'Social media graphics and posts', 'marketing', 4),
        
        -- Audio Generation
        ('voice_synthesis', 'Text-to-speech and voice generation', 'audio', 4),
        ('music_generation', 'AI-generated music and sounds', 'audio', 10),
        ('podcast_editing', 'Podcast production and editing', 'audio', 6),
        
        -- Video Generation
        ('video_generation', 'AI-generated video content', 'video', 15),
        ('video_editing', 'Video editing and post-production', 'video', 10),
        ('animation', 'Animated content creation', 'video', 20),
        
        -- Data Processing
        ('data_analysis', 'Data analysis and insights', 'analytics', 5),
        ('sentiment_analysis', 'Text sentiment and emotion analysis', 'analytics', 2),
        ('keyword_research', 'SEO and keyword research', 'marketing', 3),
        ('competitor_analysis', 'Market and competitor research', 'analytics', 8);
    """))
    
    # 4. PROVIDER MODELS
    op.execute(text("""
        INSERT INTO provider_models (provider, model_name, task_types, cost_per_credit, is_active) VALUES
        -- OpenAI Models
        ('openai', 'gpt-4o', '["text_generation", "copywriting", "blog_writing", "social_media", "email_writing", "code_generation", "summarization"]', 5, true),
        ('openai', 'gpt-4o-mini', '["text_generation", "copywriting", "social_media", "summarization", "translation"]', 1, true),
        ('openai', 'gpt-3.5-turbo', '["text_generation", "copywriting", "social_media", "translation"]', 1, true),
        ('openai', 'dall-e-3', '["image_generation", "logo_design", "product_images", "social_graphics"]', 8, true),
        ('openai', 'dall-e-2', '["image_generation", "social_graphics"]', 4, true),
        ('openai', 'tts-1', '["voice_synthesis"]', 3, true),
        ('openai', 'whisper-1', '["podcast_editing"]', 2, true),
        
        -- Anthropic Models
        ('anthropic', 'claude-3-5-sonnet-20241022', '["text_generation", "copywriting", "blog_writing", "code_generation", "data_analysis"]', 6, true),
        ('anthropic', 'claude-3-5-haiku-20241022', '["text_generation", "social_media", "summarization", "translation"]', 2, true),
        ('anthropic', 'claude-3-opus-20240229', '["text_generation", "copywriting", "blog_writing", "code_generation"]', 10, true),
        
        -- Google Models
        ('google', 'gemini-pro', '["text_generation", "copywriting", "code_generation", "data_analysis"]', 3, true),
        ('google', 'gemini-pro-vision', '["text_generation", "image_editing", "data_analysis"]', 4, true),
        ('google', 'gemini-flash', '["text_generation", "social_media", "translation"]', 1, true),
        
        -- Mistral Models
        ('mistral', 'mistral-large-latest', '["text_generation", "copywriting", "code_generation"]', 4, true),
        ('mistral', 'mistral-medium-latest', '["text_generation", "social_media"]', 2, true),
        ('mistral', 'mistral-small-latest', '["text_generation", "translation"]', 1, true),
        
        -- Stability AI Models
        ('stability', 'stable-diffusion-xl', '["image_generation", "product_images", "social_graphics"]', 6, true),
        ('stability', 'stable-diffusion-3', '["image_generation", "logo_design"]', 8, true),
        
        -- ElevenLabs Models
        ('elevenlabs', 'eleven-multilingual-v2', '["voice_synthesis"]', 4, true),
        ('elevenlabs', 'eleven-turbo-v2', '["voice_synthesis"]', 2, true),
        
        -- Replicate Models
        ('replicate', 'music-gen', '["music_generation"]', 12, true),
        ('replicate', 'runway-ml', '["video_generation", "video_editing"]', 20, true);
    """))
    
    # 5. AGENT CATEGORIES
    op.execute(text("""
        INSERT INTO agent_categories (category_name, description, sort_order, is_active) VALUES
        ('marketing', 'Marketing automation and content creation', 1, true),
        ('content', 'Content creation and writing assistants', 2, true),
        ('design', 'Visual design and creative automation', 3, true),
        ('analytics', 'Data analysis and business intelligence', 4, true),
        ('development', 'Development and technical automation', 5, true),
        ('social_media', 'Social media management and posting', 6, true),
        ('customer_service', 'Customer support and engagement', 7, true),
        ('research', 'Market research and competitive analysis', 8, true),
        ('productivity', 'General productivity and workflow automation', 9, true),
        ('e_commerce', 'E-commerce and sales automation', 10, true);
    """))
    
    # 6. AGENT TYPES (linked to categories)
    op.execute(text("""
        INSERT INTO agent_types (type_name, category_id, description, default_config) VALUES
        -- Marketing (category_id = 1)
        ('campaign_manager', 1, 'Automated marketing campaign creation and management', '{"max_campaigns": 5, "channels": ["email", "social"], "automation": true}'),
        ('content_scheduler', 1, 'Social media content scheduling and posting', '{"platforms": ["twitter", "linkedin", "facebook"], "auto_post": false}'),
        ('email_marketer', 1, 'Email campaign creation and automation', '{"list_management": true, "a_b_testing": true, "analytics": true}'),
        ('ad_optimizer', 1, 'Advertising campaign optimization', '{"platforms": ["google_ads", "facebook_ads"], "auto_optimize": false}'),
        
        -- Content (category_id = 2)
        ('blog_writer', 2, 'Automated blog post generation', '{"tone": "professional", "length": "medium", "seo_optimized": true}'),
        ('copywriter', 2, 'Marketing copy and sales content creation', '{"styles": ["persuasive", "informative", "conversational"]}'),
        ('social_writer', 2, 'Social media content creation', '{"platforms": ["twitter", "linkedin"], "hashtags": true, "trending": true}'),
        ('translator', 2, 'Multi-language content translation', '{"languages": ["en", "es", "fr", "de", "pt"], "context_aware": true}'),
        
        -- Design (category_id = 3)
        ('graphic_designer', 3, 'Automated graphic design creation', '{"formats": ["social", "web", "print"], "brand_consistency": true}'),
        ('logo_creator', 3, 'Logo and brand identity generation', '{"styles": ["modern", "classic", "minimal"], "variations": 5}'),
        ('image_editor', 3, 'Image enhancement and manipulation', '{"filters": true, "background_removal": true, "resize": true}'),
        
        -- Analytics (category_id = 4)
        ('data_analyst', 4, 'Business data analysis and insights', '{"visualizations": true, "predictions": false, "reports": true}'),
        ('seo_analyzer', 4, 'SEO analysis and optimization', '{"keyword_research": true, "competitor_analysis": true, "recommendations": true}'),
        ('social_monitor', 4, 'Social media monitoring and analysis', '{"sentiment": true, "engagement": true, "trends": true}'),
        
        -- Development (category_id = 5)
        ('code_generator', 5, 'Programming code generation and assistance', '{"languages": ["python", "javascript", "sql"], "documentation": true}'),
        ('api_builder', 5, 'API development and integration', '{"rest": true, "graphql": false, "documentation": true}'),
        ('test_creator', 5, 'Automated test generation', '{"unit_tests": true, "integration_tests": false, "coverage": true}'),
        
        -- Social Media (category_id = 6)
        ('social_manager', 6, 'Comprehensive social media management', '{"scheduling": true, "engagement": false, "analytics": true}'),
        ('influencer_finder', 6, 'Influencer research and outreach', '{"platforms": ["instagram", "tiktok", "youtube"], "criteria": "engagement"}'),
        ('hashtag_optimizer', 6, 'Hashtag research and optimization', '{"trending": true, "niche_specific": true, "performance_tracking": true}'),
        
        -- Customer Service (category_id = 7)
        ('support_bot', 7, 'Customer support automation', '{"24_7": true, "multilingual": false, "escalation": true}'),
        ('feedback_analyzer', 7, 'Customer feedback analysis', '{"sentiment": true, "categorization": true, "action_items": true}'),
        
        -- Research (category_id = 8)
        ('market_researcher', 8, 'Market research and competitive analysis', '{"industries": [], "depth": "medium", "sources": ["web", "social"]}'),
        ('trend_analyzer', 8, 'Industry trends and predictions', '{"time_horizon": "6_months", "confidence_level": "medium"}'),
        
        -- Productivity (category_id = 9)
        ('task_manager', 9, 'Task and project management automation', '{"priority_sorting": true, "deadline_tracking": true, "notifications": true}'),
        ('meeting_assistant', 9, 'Meeting management and note-taking', '{"transcription": false, "action_items": true, "follow_up": true}'),
        
        -- E-commerce (category_id = 10)
        ('product_describer', 10, 'Product description generation', '{"seo_optimized": true, "multiple_formats": true, "features_benefits": true}'),
        ('price_optimizer', 10, 'Dynamic pricing optimization', '{"competitor_monitoring": true, "demand_analysis": false, "auto_adjust": false}'),
        ('inventory_manager', 10, 'Inventory management automation', '{"reorder_alerts": true, "demand_forecasting": false, "supplier_integration": false}');
    """))
    
    # 7. CAMPAIGN TYPES
    op.execute(text("""
        INSERT INTO campaign_types (type_name, description, default_channels, estimated_duration_days) VALUES
        ('brand_awareness', 'Build brand recognition and visibility', '["social_media", "display_ads", "content_marketing"]', 30),
        ('lead_generation', 'Generate qualified leads for sales', '["email", "social_media", "search_ads", "content_marketing"]', 45),
        ('product_launch', 'Launch new products or services', '["email", "social_media", "pr", "influencer", "paid_ads"]', 60),
        ('customer_retention', 'Retain and engage existing customers', '["email", "social_media", "content_marketing", "loyalty"]', 90),
        ('sales_promotion', 'Drive immediate sales with promotions', '["email", "social_media", "paid_ads", "sms"]', 14),
        ('content_marketing', 'Educational and value-driven content', '["blog", "social_media", "email", "video"]', 90),
        ('event_promotion', 'Promote events and webinars', '["email", "social_media", "paid_ads", "partnerships"]', 30),
        ('social_media', 'Focused social media engagement', '["facebook", "instagram", "twitter", "linkedin", "tiktok"]', 30),
        ('email_nurturing', 'Email-based lead nurturing sequences', '["email", "marketing_automation"]', 60),
        ('influencer_marketing', 'Collaborate with influencers', '["influencer", "social_media", "content_marketing"]', 45),
        ('seo_content', 'SEO-focused content creation', '["blog", "website", "social_media"]', 120),
        ('holiday_seasonal', 'Seasonal and holiday campaigns', '["email", "social_media", "paid_ads", "content_marketing"]', 21),
        ('crisis_management', 'Reputation and crisis management', '["pr", "social_media", "email", "media_outreach"]', 7),
        ('customer_feedback', 'Collect and act on customer feedback', '["email", "social_media", "surveys", "reviews"]', 30),
        ('rebranding', 'Company or product rebranding', '["pr", "social_media", "email", "content_marketing", "paid_ads"]', 90);
    """))


def downgrade() -> None:
    """Downgrade schema - Remove all seed data."""
    
    # Clear all lookup tables in reverse dependency order
    op.execute(text("DELETE FROM campaign_types"))
    op.execute(text("DELETE FROM agent_types"))
    op.execute(text("DELETE FROM agent_categories"))
    op.execute(text("DELETE FROM provider_models"))
    op.execute(text("DELETE FROM task_types"))
    op.execute(text("DELETE FROM ai_providers"))
    op.execute(text("DELETE FROM subscription_tiers"))
