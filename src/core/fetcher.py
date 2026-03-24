"""RSS feed fetching for the Agentic Digest."""

import feedparser
from datetime import datetime, timedelta
from dateutil import parser as dateparser
from .models import Article

# Tier-organized feed configuration
FEEDS = {
    # =========================================================================
    # TIER 1: Builder Signal — 100 sources
    # =========================================================================

# =========================================================================
    # CATEGORY 1: AI LABS & MODEL PROVIDERS (22 sources)
    # =========================================================================

    "Anthropic Blog": {
        "url": "https://raw.githubusercontent.com/taobojlen/anthropic-rss-feed/main/anthropic_news_rss.xml",
        "tier": 1,
        "focus": "Claude model releases, system prompts, safety research, and product updates from Anthropic"
    },
    "Anthropic Engineering Blog": {
        "url": "https://raw.githubusercontent.com/conoro/anthropic-engineering-rss-feed/main/anthropic_engineering_rss.xml",
        "tier": 1,
        "focus": "Production reliability engineering, prompt engineering patterns, and Claude API best practices"
    },
    "OpenAI Blog": {
        "url": "https://openai.com/blog/rss.xml",
        "tier": 1,
        "focus": "GPT model releases, API updates, safety research, and product announcements"
    },
    "Google DeepMind Blog": {
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": 1,
        "focus": "Gemini models, AlphaFold, frontier research in reasoning, multimodal AI"
    },
    "Google AI Blog": {
        "url": "https://blog.google/technology/ai/rss/",
        "tier": 1,
        "focus": "Google AI product integrations, Gemini ecosystem, AI infrastructure announcements"
    },
    "Meta AI Research": {
        "url": "https://ai.meta.com/blog/rss/",
        "tier": 1,
        "focus": "Llama models, open-source AI research, PyTorch ecosystem updates"
    },
    "Hugging Face Blog": {
        "url": "https://huggingface.co/blog/feed.xml",
        "tier": 1,
        "focus": "Open-source model releases, Transformers library, community model benchmarks, Spaces"
    },
    "Stability AI Blog": {
        "url": "https://stability.ai/news/feed/",
        "tier": 1,
        "focus": "Stable Diffusion models, open-source generative AI, image/video/audio generation"
    },
    "Cohere Blog": {
        "url": "https://cohere.com/blog/rss/",
        "tier": 1,
        "focus": "Enterprise LLMs, RAG implementations, Command models, embedding best practices"
    },
    "Mistral AI Blog": {
        "url": "https://mistral.ai/feed.xml",
        "tier": 1,
        "focus": "Open-weight models, Mixtral MoE architectures, European AI infrastructure"
    },
    "Together AI Blog": {
        "url": "https://www.together.ai/blog/rss.xml",
        "tier": 1,
        "focus": "Open-source model serving, fine-tuning infrastructure, inference optimization"
    },
    "Fireworks AI Blog": {
        "url": "https://fireworks.ai/blog/rss.xml",
        "tier": 1,
        "focus": "Fast inference infrastructure, function calling, compound AI systems"
    },
    "Groq Blog": {
        "url": "https://groq.com/feed/",
        "tier": 1,
        "focus": "LPU inference hardware, ultra-low-latency AI serving, GroqCloud platform"
    },
    "Cerebras Blog": {
        "url": "https://cerebras.ai/feed/",
        "tier": 1,
        "focus": "Wafer-scale AI chips, fast inference, large-scale model training hardware"
    },
    "EleutherAI Blog": {
        "url": "https://blog.eleuther.ai/index.xml",
        "tier": 1,
        "focus": "Open-source LLM research, GPT-NeoX, evaluation harness, alignment research"
    },
    "AI21 Labs Blog": {
        "url": "https://www.ai21.com/blog/rss.xml",
        "tier": 1,
        "focus": "Jamba models, enterprise AI writing, task-specific language models"
    },
    "Reka AI Blog": {
        "url": "https://reka.ai/feed.xml",
        "tier": 1,
        "focus": "Multimodal foundation models, video understanding, Reka Core/Flash/Edge"
    },
    "Lightning AI Blog": {
        "url": "https://lightning.ai/pages/feed/",
        "tier": 1,
        "focus": "PyTorch Lightning, LitGPT, training infrastructure, model deployment studios"
    },
    "NVIDIA AI Blog": {
        "url": "https://developer.nvidia.com/blog/feed/",
        "tier": 1,
        "focus": "GPU computing for AI, CUDA, TensorRT, NeMo framework, inference optimization"
    },
    "AWS Machine Learning Blog": {
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "tier": 1,
        "focus": "SageMaker, Bedrock, AWS AI services, production ML deployment patterns"
    },
    "Microsoft AI Blog": {
        "url": "https://blogs.microsoft.com/ai/feed/",
        "tier": 1,
        "focus": "Azure OpenAI Service, Copilot stack, AI infrastructure, Semantic Kernel"
    },
    "Microsoft Research Blog": {
        "url": "https://www.microsoft.com/en-us/research/feed/",
        "tier": 1,
        "focus": "Frontier AI research, AutoGen, Phi models, reasoning and agents research"
    },

    # =========================================================================
    # CATEGORY 2: AGENT FRAMEWORK TEAMS (16 sources)
    # =========================================================================

    "LangChain Blog": {
        "url": "https://blog.langchain.com/rss/",
        "tier": 1,
        "focus": "LangGraph agent architectures, LangSmith observability, production agent patterns"
    },
    "LlamaIndex Blog (Medium)": {
        "url": "https://medium.com/feed/llamaindex-blog",
        "tier": 1,
        "focus": "RAG optimization, data ingestion pipelines, LlamaCloud, agent workflows"
    },
    "CrewAI Blog": {
        "url": "https://blog.crewai.com/feed/",
        "tier": 1,
        "focus": "Multi-agent orchestration, role-based agent teams, CrewAI framework patterns"
    },
    "Haystack by deepset Blog": {
        "url": "https://haystack.deepset.ai/blog/feed.xml",
        "tier": 1,
        "focus": "Open-source AI orchestration, RAG pipelines, component-based agent design"
    },
    "Vercel Blog": {
        "url": "https://vercel.com/atom",
        "tier": 1,
        "focus": "Vercel AI SDK, streaming AI interfaces, Next.js AI integration patterns"
    },
    "Pydantic Blog": {
        "url": "https://blog.pydantic.dev/feed/",
        "tier": 1,
        "focus": "Pydantic AI agent framework, structured output validation, Python type safety for LLMs"
    },
    "Semantic Kernel Blog (Microsoft)": {
        "url": "https://devblogs.microsoft.com/semantic-kernel/feed/",
        "tier": 1,
        "focus": "Microsoft Semantic Kernel SDK, AI plugin architecture, .NET/Python agent development"
    },
    "Gradio Blog": {
        "url": "https://www.gradio.app/blog/rss.xml",
        "tier": 1,
        "focus": "ML demo interfaces, Hugging Face Spaces integration, rapid AI app prototyping"
    },
    "Langfuse Blog": {
        "url": "https://langfuse.com/blog/feed.xml",
        "tier": 1,
        "focus": "LLM observability, tracing, prompt management, open-source AI monitoring"
    },
    "BentoML Blog": {
        "url": "https://www.bentoml.com/blog/rss.xml",
        "tier": 1,
        "focus": "Model serving, BentoCloud deployment, LLM inference infrastructure"
    },
    "dspy Blog (Stanford NLP)": {
        "url": "https://dspy.ai/feed.xml",
        "tier": 1,
        "focus": "Programmatic prompt optimization, declarative language model pipelines"
    },
    "Instructor Blog (by Jason Liu)": {
        "url": "https://python.useinstructor.com/blog/feed.xml",
        "tier": 1,
        "focus": "Structured output extraction from LLMs, Pydantic + LLM patterns"
    },
    "Cursor Blog": {
        "url": "https://cursor.com/rss.xml",
        "tier": 1,
        "focus": "AI-native code editor, coding agent UX, agentic development workflows"
    },
    "GitHub Blog (AI/ML)": {
        "url": "https://github.blog/ai-and-ml/feed/",
        "tier": 1,
        "focus": "GitHub Copilot, AI-powered development tools, coding agent infrastructure"
    },
    "Sourcegraph Blog": {
        "url": "https://sourcegraph.com/blog/feed.atom",
        "tier": 1,
        "focus": "Cody AI assistant, code intelligence, large-scale code search for agents"
    },
    "Ollama Blog": {
        "url": "https://ollama.com/blog/feed",
        "tier": 1,
        "focus": "Local LLM serving, model library management, on-device AI inference"
    },

    # =========================================================================
    # CATEGORY 3: INDIVIDUAL BUILDERS / ENGINEERS (27 sources)
    # =========================================================================

    "Simon Willison's Weblog": {
        "url": "https://simonwillison.net/atom/everything/",
        "tier": 1,
        "focus": "Daily LLM tool reviews, prompt engineering, Datasette, practical AI applications"
    },
    "Andrej Karpathy Blog": {
        "url": "https://karpathy.bearblog.dev/feed/",
        "tier": 1,
        "focus": "Deep learning fundamentals, LLM training insights, AI education from former OpenAI/Tesla"
    },
    "Chip Huyen Blog": {
        "url": "https://huyenchip.com/feed.xml",
        "tier": 1,
        "focus": "AI engineering platforms, MLOps, production AI system design, agent architectures"
    },
    "Lilian Weng (Lil'Log)": {
        "url": "https://lilianweng.github.io/index.xml",
        "tier": 1,
        "focus": "Definitive technical deep dives on agents, reward hacking, diffusion models, RLHF"
    },
    "Eugene Yan": {
        "url": "https://eugeneyan.com/rss/",
        "tier": 1,
        "focus": "Production ML systems, LLM evals, RAG patterns, RecSys at scale (Anthropic)"
    },
    "Sebastian Raschka (Ahead of AI)": {
        "url": "https://magazine.sebastianraschka.com/feed",
        "tier": 1,
        "focus": "LLM architecture comparisons, fine-tuning with LoRA, pre/post-training paradigms"
    },
    "Hamel Husain Blog": {
        "url": "https://hamel.dev/feed_rss_created.xml",
        "tier": 1,
        "focus": "Applied AI engineering, LLM evaluation, coding agents, practical LLM course design"
    },
    "Jay Alammar Blog": {
        "url": "https://jalammar.github.io/feed.xml",
        "tier": 1,
        "focus": "Visual explanations of Transformers, attention mechanisms, LLM internals"
    },
    "Vicki Boykis Blog": {
        "url": "https://vickiboykis.com/index.xml",
        "tier": 1,
        "focus": "Embeddings at scale, vector search engineering, ML infrastructure (ex-Mozilla AI)"
    },
    "Nicholas Carlini Blog": {
        "url": "https://nicholas.carlini.com/writing/feed.xml",
        "tier": 1,
        "focus": "LLM security research, adversarial ML, practical AI usage from Google DeepMind researcher"
    },
    "Philipp Schmid Blog": {
        "url": "https://www.philschmid.de/feed.xml",
        "tier": 1,
        "focus": "Hugging Face tutorials, LLM deployment guides, fine-tuning practical walkthroughs"
    },
    "Nathan Lambert (Interconnects)": {
        "url": "https://www.interconnects.ai/feed",
        "tier": 1,
        "focus": "Open model training, RLHF research, post-training paradigms, AI2 OLMo insights"
    },
    "Latent Space (swyx & Alessio)": {
        "url": "https://www.latent.space/feed",
        "tier": 1,
        "focus": "AI engineer interviews, framework deep dives, industry analysis, AI engineering trends"
    },
    "Ethan Mollick (One Useful Thing)": {
        "url": "https://www.oneusefulthing.org/feed",
        "tier": 1,
        "focus": "Practical AI usage patterns, education/work implications, Wharton professor perspective"
    },
    "Cameron Wolfe (Deep Learning Focus)": {
        "url": "https://cameronrwolfe.substack.com/feed",
        "tier": 1,
        "focus": "Deep dives into AI research papers, LLM architectures explained, Netflix ML research"
    },
    "The Gradient": {
        "url": "https://thegradientpub.substack.com/feed",
        "tier": 1,
        "focus": "AI research interviews and analysis from Stanford AI Lab researchers"
    },
    "TheSequence": {
        "url": "https://thesequence.substack.com/feed",
        "tier": 1,
        "focus": "Concise ML/AI technical summaries, paper breakdowns, industry analysis"
    },
    "The Algorithmic Bridge": {
        "url": "https://thealgorithmicbridge.substack.com/feed",
        "tier": 1,
        "focus": "AI capabilities analysis, reasoning about AI progress and limitations"
    },
    "Colah's Blog": {
        "url": "https://colah.github.io/rss.xml",
        "tier": 1,
        "focus": "Neural network visualizations, deep learning intuitions, Anthropic interpretability"
    },
    "fast.ai Blog": {
        "url": "https://www.fast.ai/index.xml",
        "tier": 1,
        "focus": "Practical deep learning, fastai library, democratizing AI education"
    },
    "Shreya Shankar Blog": {
        "url": "https://www.sh-reya.com/blog/rss.xml",
        "tier": 1,
        "focus": "LLM data management, AI/HCI research, production ML pipelines"
    },
    "Jason Liu (jxnl) Blog": {
        "url": "https://jxnl.co/writing/feed.xml",
        "tier": 1,
        "focus": "Instructor library creator, structured LLM outputs, AI consulting insights"
    },
    "Hamel Husain (Applied LLMs)": {
        "url": "https://hamelhusain.substack.com/feed",
        "tier": 1,
        "focus": "LLM evaluation courses, applied AI engineering newsletter, Parlance Labs"
    },
    "Last Week in AI": {
        "url": "https://lastweekin.ai/feed",
        "tier": 1,
        "focus": "Weekly AI news roundup covering research, industry, and policy developments"
    },
    "Synced Review": {
        "url": "https://syncedreview.com/feed/",
        "tier": 1,
        "focus": "AI research paper summaries, industry news, Chinese and global AI developments"
    },
    "Machine Learning Mastery": {
        "url": "https://machinelearningmastery.com/blog/feed/",
        "tier": 1,
        "focus": "Practical ML/DL tutorials, step-by-step implementation guides, LLM how-tos"
    },
    "MarkTechPost": {
        "url": "https://www.marktechpost.com/feed/",
        "tier": 1,
        "focus": "AI research paper breakdowns, new model announcements, tool reviews"
    },

    # =========================================================================
    # CATEGORY 4: INFRASTRUCTURE & DEVTOOLS (20 sources)
    # =========================================================================

    "Weights & Biases (Fully Connected)": {
        "url": "https://wandb.ai/fully-connected/rss.xml",
        "tier": 1,
        "focus": "Experiment tracking, model evaluation, LLM fine-tuning workflows, Weave tracing"
    },
    "Replicate Blog": {
        "url": "https://replicate.com/blog/rss",
        "tier": 1,
        "focus": "Cloud model inference, open-source model hosting, serverless GPU deployment"
    },
    "Modal Blog": {
        "url": "https://modal.com/blog/feed.xml",
        "tier": 1,
        "focus": "Serverless GPU infrastructure, Python cloud functions, LLM fine-tuning at scale"
    },
    "Pinecone Blog": {
        "url": "https://www.pinecone.io/blog/feed/",
        "tier": 1,
        "focus": "Vector database optimization, RAG architectures, semantic search at production scale"
    },
    "Weaviate Blog": {
        "url": "https://weaviate.io/blog/feed.xml",
        "tier": 1,
        "focus": "Vector search, hybrid retrieval, RAG pipelines, multi-tenant vector databases"
    },
    "Qdrant Blog": {
        "url": "https://qdrant.tech/blog/feed.xml",
        "tier": 1,
        "focus": "Vector similarity search, filtering, hybrid search, edge deployment"
    },
    "Chroma Blog": {
        "url": "https://www.trychroma.com/blog/feed.xml",
        "tier": 1,
        "focus": "Embedded vector database, local-first AI, lightweight RAG infrastructure"
    },
    "Zilliz (Milvus) Blog": {
        "url": "https://zilliz.com/blog/feed",
        "tier": 1,
        "focus": "Milvus vector database, billion-scale vector search, GPU-accelerated similarity"
    },
    "Neptune.ai Blog": {
        "url": "https://neptune.ai/blog/feed/",
        "tier": 1,
        "focus": "MLOps best practices, experiment management, model registry workflows"
    },
    "Databricks Blog": {
        "url": "https://www.databricks.com/feed",
        "tier": 1,
        "focus": "Lakehouse AI, MLflow, Unity Catalog, Mosaic ML training infrastructure"
    },
    "Anyscale (Ray) Blog": {
        "url": "https://www.anyscale.com/blog/rss.xml",
        "tier": 1,
        "focus": "Ray distributed computing, scalable LLM training/serving, vLLM integration"
    },
    "Unsloth AI Blog": {
        "url": "https://unsloth.ai/blog/rss.xml",
        "tier": 1,
        "focus": "2x faster LLM fine-tuning, memory optimization, QLoRA/LoRA acceleration"
    },
    "Helicone Blog": {
        "url": "https://www.helicone.ai/blog/rss.xml",
        "tier": 1,
        "focus": "LLM observability, cost tracking, prompt monitoring, production AI debugging"
    },
    "Braintrust Blog": {
        "url": "https://www.braintrust.dev/blog/feed.xml",
        "tier": 1,
        "focus": "AI evaluation platform, LLM testing, prompt playground, logging infrastructure"
    },
    "Portkey AI Blog": {
        "url": "https://portkey.ai/blog/rss.xml",
        "tier": 1,
        "focus": "AI gateway, LLM routing, fallbacks, caching, production AI reliability"
    },
    "LiteLLM Blog": {
        "url": "https://www.litellm.ai/blog/feed.xml",
        "tier": 1,
        "focus": "Unified LLM API proxy, multi-provider routing, cost management"
    },
    "Axolotl AI Blog": {
        "url": "https://axolotl.ai/blog/feed.xml",
        "tier": 1,
        "focus": "Open-source LLM fine-tuning framework, training recipes, FSDP/DeepSpeed"
    },
    "vLLM Blog": {
        "url": "https://blog.vllm.ai/feed.xml",
        "tier": 1,
        "focus": "High-throughput LLM serving, PagedAttention, continuous batching, inference speed"
    },
    "Firecrawl Blog": {
        "url": "https://www.firecrawl.dev/blog/feed.xml",
        "tier": 1,
        "focus": "Web scraping for LLMs, structured data extraction, crawling for RAG pipelines"
    },
    "Supabase Blog": {
        "url": "https://supabase.com/blog/rss.xml",
        "tier": 1,
        "focus": "pgvector integration, edge functions for AI, real-time AI app infrastructure"
    },

    # =========================================================================
    # CATEGORY 5: OPEN SOURCE PROJECTS (5 sources)
    # =========================================================================

    "PyTorch Blog": {
        "url": "https://pytorch.org/blog/feed.xml",
        "tier": 1,
        "focus": "PyTorch releases, ExecuTorch mobile, torch.compile, distributed training"
    },
    "TensorFlow Blog": {
        "url": "https://blog.tensorflow.org/feeds/posts/default?alt=rss",
        "tier": 1,
        "focus": "TensorFlow/Keras updates, TFLite, on-device ML, JAX integration"
    },
    "Hugging Face Daily Papers": {
        "url": "https://huggingface-papers-rss.yfacialgreen.workers.dev/rss",
        "tier": 1,
        "focus": "Daily curated ML research papers trending on Hugging Face, community-voted"
    },
    "MLflow Blog": {
        "url": "https://mlflow.org/blog/feed.xml",
        "tier": 1,
        "focus": "MLflow releases, experiment tracking, model registry, LLM evaluation tools"
    },
    "Distill.pub": {
        "url": "https://distill.pub/rss.xml",
        "tier": 1,
        "focus": "Interactive visual explanations of ML concepts, interpretability research"
    },

    # =========================================================================
    # CATEGORY 6: RESEARCH LABS & ACADEMIC (10 sources)
    # =========================================================================

    "ArXiv CS.AI": {
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "tier": 3,
        "focus": "Latest AI research papers: agents, reasoning, planning, knowledge representation"
    },
    "ArXiv CS.LG (Machine Learning)": {
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "tier": 3,
        "focus": "Machine learning research: architectures, training methods, optimization"
    },
    "ArXiv CS.CL (Computation & Language)": {
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "tier": 3,
        "focus": "NLP research: LLMs, prompting, RLHF, instruction tuning, evaluation"
    },
    "Berkeley AI Research (BAIR) Blog": {
        "url": "https://bair.berkeley.edu/blog/feed.xml",
        "tier": 1,
        "focus": "Cutting-edge AI research from UC Berkeley: agents, robotics, reasoning, RL"
    },
    "Stanford CRFM Blog": {
        "url": "https://crfm.stanford.edu/feed.xml",
        "tier": 1,
        "focus": "Foundation model research, HELM benchmarks, responsible AI evaluation"
    },
    "CMU Machine Learning Blog": {
        "url": "https://blog.ml.cmu.edu/feed/",
        "tier": 1,
        "focus": "Carnegie Mellon ML research: optimization, generalization, AI theory"
    },
    "MIT News (Machine Learning)": {
        "url": "https://news.mit.edu/topic/mitmachine-learning-rss.xml",
        "tier": 1,
        "focus": "MIT AI/ML research breakthroughs, CSAIL updates, interdisciplinary AI"
    },
    "Google Research Blog": {
        "url": "https://blog.research.google/feeds/posts/default?alt=rss",
        "tier": 1,
        "focus": "Google Research papers, Transformer advances, multimodal AI, efficiency"
    },
    "Allen Institute for AI (AI2) Blog": {
        "url": "https://blog.allenai.org/feed",
        "tier": 1,
        "focus": "OLMo open models, Semantic Scholar, WildBench, open-source AI research"
    },
    "Towards Data Science": {
        "url": "https://towardsdatascience.com/feed",
        "tier": 1,
        "focus": "Community-written ML/AI tutorials, LLM implementation guides, data science"
    },

    # =========================================================================
    # TIER 2: Curated Daily News — 100 sources
    # =========================================================================

    # --- AI Newsletters (40) ---
    "The Rundown AI": {
        "url": "https://www.therundown.ai/feed",
        "tier": 2,
        "focus": "Daily AI news for founders and executives"
    },
    "GenAI.works": {
        "url": "https://newsletter.genai.works/feed",
        "tier": 2,
        "focus": "Daily generative AI news and tools"
    },
    "AI++ Newsletter": {
        "url": "https://aiplusplus.substack.com/feed",
        "tier": 2,
        "focus": "Agents, MCP, developer tools"
    },
    "Superhuman AI": {
        "url": "https://www.superhuman.ai/feed",
        "tier": 2,
        "focus": "AI tools and productivity, 3 min format"
    },
    "Ben's Bites": {
        "url": "https://bensbites.beehiiv.com/feed",
        "tier": 2,
        "focus": "Daily AI news digest for builders"
    },
    "Import AI (Jack Clark)": {
        "url": "https://importai.substack.com/feed",
        "tier": 2,
        "focus": "Weekly AI research and policy roundup"
    },
    "TLDR AI": {
        "url": "https://tldr.tech/ai/rss",
        "tier": 2,
        "focus": "Bite-sized daily AI news and research"
    },
    "The Neuron": {
        "url": "https://www.theneurondaily.com/feed",
        "tier": 2,
        "focus": "Daily AI news for non-technical leaders"
    },
    "AI Breakfast": {
        "url": "https://aibreakfast.beehiiv.com/feed",
        "tier": 2,
        "focus": "Morning AI news briefing"
    },
    "Ahead of AI (Sebastian Raschka)": {
        "url": "https://magazine.sebastianraschka.com/feed",
        "tier": 2,
        "focus": "ML research, LLMs, practical deep learning"
    },
    "The Batch (Andrew Ng)": {
        "url": "https://www.deeplearning.ai/the-batch/feed/",
        "tier": 2,
        "focus": "AI industry analysis, education, trends"
    },
    "AI Supremacy": {
        "url": "https://aisupremacy.substack.com/feed",
        "tier": 2,
        "focus": "AI industry news and market analysis"
    },
    "The AI Valley": {
        "url": "https://theaivalley.beehiiv.com/feed",
        "tier": 2,
        "focus": "AI tools, prompts, and news for professionals"
    },
    "AI Tool Report": {
        "url": "https://aitoolreport.beehiiv.com/feed",
        "tier": 2,
        "focus": "Daily AI tool reviews and news"
    },
    "Mindstream AI": {
        "url": "https://mindstream.news/feed",
        "tier": 2,
        "focus": "Daily AI newsletter with actionable insights"
    },
    "Last Week in AI": {
        "url": "https://lastweekin.ai/feed",
        "tier": 2,
        "focus": "Weekly roundup of AI news and hype"
    },
    "Davis Summarizes Papers": {
        "url": "https://dblalock.substack.com/feed",
        "tier": 2,
        "focus": "Concise ML paper summaries"
    },
    "The Gradient": {
        "url": "https://thegradient.pub/rss/",
        "tier": 2,
        "focus": "AI research perspectives and analysis"
    },
    "AlphaSignal": {
        "url": "https://alphasignal.beehiiv.com/feed",
        "tier": 2,
        "focus": "Curated AI research summaries"
    },
    "AI Tidbits": {
        "url": "https://aitidbits.substack.com/feed",
        "tier": 2,
        "focus": "Weekly AI developments and commentary"
    },
    "Interconnects (Nathan Lambert)": {
        "url": "https://www.interconnects.ai/feed",
        "tier": 2,
        "focus": "AI policy, RLHF, open-source models"
    },
    "The Algorithmic Bridge": {
        "url": "https://thealgorithmicbridge.substack.com/feed",
        "tier": 2,
        "focus": "AI impact on society and culture"
    },
    "AI Snake Oil": {
        "url": "https://www.aisnakeoil.com/feed",
        "tier": 2,
        "focus": "Critical analysis of AI claims and hype"
    },
    "Uncharted Territories": {
        "url": "https://unchartedterritories.tomaspueyo.com/feed",
        "tier": 2,
        "focus": "AI impact on society and geopolitics"
    },
    "Exponential View (Azeem Azhar)": {
        "url": "https://www.exponentialview.co/feed",
        "tier": 2,
        "focus": "Exponential tech trends including AI"
    },
    "AI Pedia Hub": {
        "url": "https://aipediahub.substack.com/feed",
        "tier": 2,
        "focus": "AI tutorials, tools, and daily updates"
    },
    "The Sequence": {
        "url": "https://thesequence.substack.com/feed",
        "tier": 2,
        "focus": "ML research and industry in 5-minute reads"
    },
    "Deep (Learning) Focus": {
        "url": "https://deeplearningfocus.substack.com/feed",
        "tier": 2,
        "focus": "Focused deep learning news and research"
    },
    "Data Machina": {
        "url": "https://datamachina.substack.com/feed",
        "tier": 2,
        "focus": "Curated data science and AI links"
    },
    "The ML Engineer": {
        "url": "https://ethical.institute/mle.html",
        "tier": 2,
        "focus": "ML engineering best practices newsletter"
    },
    "NLP News (Sebastian Ruder)": {
        "url": "https://newsletter.ruder.io/feed",
        "tier": 2,
        "focus": "NLP research highlights and analysis"
    },
    "Machine Learning Mastery": {
        "url": "https://machinelearningmastery.com/feed/",
        "tier": 2,
        "focus": "Practical ML tutorials and guides"
    },
    "Weights & Biases Blog": {
        "url": "https://wandb.ai/fully-connected/rss.xml",
        "tier": 2,
        "focus": "MLOps, experiment tracking, best practices"
    },
    "Towards Data Science (Medium)": {
        "url": "https://towardsdatascience.com/feed",
        "tier": 2,
        "focus": "Community data science and AI articles"
    },
    "Towards AI": {
        "url": "https://pub.towardsai.net/feed",
        "tier": 2,
        "focus": "AI tutorials, news, and research"
    },
    "Analytics Vidhya": {
        "url": "https://www.analyticsvidhya.com/feed/",
        "tier": 2,
        "focus": "Data science and AI tutorials"
    },
    "KDnuggets": {
        "url": "https://www.kdnuggets.com/feed",
        "tier": 2,
        "focus": "Data science, ML, AI news and tutorials"
    },
    "Data Science Central": {
        "url": "https://www.datasciencecentral.com/feed/",
        "tier": 2,
        "focus": "Data science community articles"
    },
    "DAIR.AI": {
        "url": "https://dair-ai.substack.com/feed",
        "tier": 2,
        "focus": "ML papers, tools, and educational content"
    },
    "Cohere Blog": {
        "url": "https://txt.cohere.com/rss/",
        "tier": 2,
        "focus": "Enterprise NLP and LLM applications"
    },

    # --- Tech News with AI Focus (30) ---
    "TechCrunch AI": {
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "tier": 2,
        "focus": "AI startup funding, launches, acquisitions"
    },
    "The Verge AI": {
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "tier": 2,
        "focus": "AI product news, industry moves"
    },
    "Wired AI": {
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "tier": 2,
        "focus": "AI features, long-form tech journalism"
    },
    "VentureBeat AI": {
        "url": "https://venturebeat.com/category/ai/feed/",
        "tier": 2,
        "focus": "Enterprise AI, transforms, industry"
    },
    "The Information": {
        "url": "https://www.theinformation.com/feed",
        "tier": 2,
        "focus": "Tech industry scoops and analysis"
    },
    "CNBC Tech": {
        "url": "https://www.cnbc.com/id/19854910/device/rss/rss.html",
        "tier": 2,
        "focus": "Technology business and market news"
    },
    "Reuters Tech": {
        "url": "https://www.reuters.com/technology/rss",
        "tier": 2,
        "focus": "Global tech and AI business news"
    },
    "Bloomberg Tech (via feed)": {
        "url": "https://feeds.bloomberg.com/technology/news.rss",
        "tier": 2,
        "focus": "Tech business, markets, and AI"
    },
    "ZDNet AI": {
        "url": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "tier": 2,
        "focus": "Enterprise AI adoption and strategy"
    },
    "InfoWorld AI": {
        "url": "https://www.infoworld.com/category/artificial-intelligence/index.rss",
        "tier": 2,
        "focus": "AI for enterprise developers"
    },
    "SiliconANGLE AI": {
        "url": "https://siliconangle.com/category/artificial-intelligence/feed/",
        "tier": 2,
        "focus": "Enterprise tech and AI coverage"
    },
    "The Register AI": {
        "url": "https://www.theregister.com/software/ai_ml/headlines.atom",
        "tier": 2,
        "focus": "Irreverent AI/ML tech news"
    },
    "Engadget AI": {
        "url": "https://www.engadget.com/tag/ai/rss.xml",
        "tier": 2,
        "focus": "Consumer AI products and gadgets"
    },
    "Mashable AI": {
        "url": "https://mashable.com/category/artificial-intelligence/rss",
        "tier": 2,
        "focus": "AI consumer tech and culture"
    },
    "Fast Company Tech": {
        "url": "https://www.fastcompany.com/technology/rss",
        "tier": 2,
        "focus": "Tech innovation and business"
    },
    "Forbes AI": {
        "url": "https://www.forbes.com/ai/feed/",
        "tier": 2,
        "focus": "AI business strategy and leadership"
    },
    "Business Insider Tech": {
        "url": "https://www.businessinsider.com/tech/rss",
        "tier": 2,
        "focus": "Tech industry business news"
    },
    "The Guardian AI": {
        "url": "https://www.theguardian.com/technology/artificialintelligenceai/rss",
        "tier": 2,
        "focus": "AI society impact, ethics, policy"
    },
    "BBC Tech": {
        "url": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "tier": 2,
        "focus": "Global tech and AI news"
    },
    "New York Times Tech": {
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
        "tier": 2,
        "focus": "Tech industry coverage and AI policy"
    },
    "Wall Street Journal Tech": {
        "url": "https://feeds.a.dj.com/rss/RSSWSJD.xml",
        "tier": 2,
        "focus": "Tech business and market analysis"
    },
    "Washington Post Tech": {
        "url": "https://feeds.washingtonpost.com/rss/business/technology",
        "tier": 2,
        "focus": "Tech policy and industry news"
    },
    "Axios AI": {
        "url": "https://api.axios.com/feed/",
        "tier": 2,
        "focus": "Smart brevity tech and AI coverage"
    },
    "Protocol / Semafor Tech": {
        "url": "https://www.semafor.com/feed/tech",
        "tier": 2,
        "focus": "Global tech news and analysis"
    },
    "Rest of World": {
        "url": "https://restofworld.org/feed/latest/",
        "tier": 2,
        "focus": "Tech impact in emerging markets"
    },
    "Tom's Hardware AI": {
        "url": "https://www.tomshardware.com/feeds/all",
        "tier": 2,
        "focus": "AI hardware, GPUs, inference chips"
    },
    "AnandTech / Tom's Hardware": {
        "url": "https://www.tomshardware.com/feeds/all",
        "tier": 2,
        "focus": "Hardware benchmarks and AI silicon"
    },
    "9to5Google AI": {
        "url": "https://9to5google.com/guides/ai/feed/",
        "tier": 2,
        "focus": "Google AI products and features"
    },
    "9to5Mac AI": {
        "url": "https://9to5mac.com/guides/apple-intelligence/feed/",
        "tier": 2,
        "focus": "Apple Intelligence and AI features"
    },
    "WindowsCentral AI": {
        "url": "https://www.windowscentral.com/feed",
        "tier": 2,
        "focus": "Microsoft Copilot and AI integration"
    },

    # --- Industry Analysts / VC Blogs (15) ---
    "a16z Blog": {
        "url": "https://a16z.com/feed/",
        "tier": 2,
        "focus": "AI investing thesis and industry analysis"
    },
    "Sequoia Capital Blog": {
        "url": "https://www.sequoiacap.com/feed/",
        "tier": 2,
        "focus": "AI market sizing and startup building"
    },
    "Y Combinator Blog": {
        "url": "https://www.ycombinator.com/blog/rss/",
        "tier": 2,
        "focus": "Startup advice, AI company trends"
    },
    "Bessemer Venture Partners": {
        "url": "https://www.bvp.com/atlas/feed.xml",
        "tier": 2,
        "focus": "Cloud and AI industry analysis"
    },
    "First Round Review": {
        "url": "https://review.firstround.com/feed.xml",
        "tier": 2,
        "focus": "Startup management and AI company building"
    },
    "Greylock Blog": {
        "url": "https://greylock.com/feed/",
        "tier": 2,
        "focus": "Enterprise AI, infrastructure investing"
    },
    "Lightspeed Blog": {
        "url": "https://lsvp.com/feed/",
        "tier": 2,
        "focus": "AI and enterprise investing insights"
    },
    "Index Ventures": {
        "url": "https://www.indexventures.com/feed",
        "tier": 2,
        "focus": "European and US AI venture insights"
    },
    "Menlo Ventures": {
        "url": "https://menlovc.com/feed/",
        "tier": 2,
        "focus": "AI market maps and investing thesis"
    },
    "Madrona Blog": {
        "url": "https://www.madrona.com/feed/",
        "tier": 2,
        "focus": "Intelligent applications and AI infra"
    },
    "Felicis Ventures Blog": {
        "url": "https://www.felicis.com/feed",
        "tier": 2,
        "focus": "AI venture capital perspectives"
    },
    "Wing VC Blog": {
        "url": "https://wing.vc/feed",
        "tier": 2,
        "focus": "AI infrastructure and enterprise"
    },
    "NFX Blog": {
        "url": "https://www.nfx.com/feed",
        "tier": 2,
        "focus": "AI startup network effects and strategy"
    },
    "CB Insights Research": {
        "url": "https://www.cbinsights.com/research/feed/",
        "tier": 2,
        "focus": "AI market data, trends, and reports"
    },
    "Crunchbase News": {
        "url": "https://news.crunchbase.com/feed/",
        "tier": 2,
        "focus": "AI startup funding data and analysis"
    },

    # --- Product/Startup News (15) ---
    "Product Hunt": {
        "url": "https://www.producthunt.com/feed",
        "tier": 2,
        "focus": "New AI product launches daily"
    },
    "Indie Hackers": {
        "url": "https://www.indiehackers.com/feed.xml",
        "tier": 2,
        "focus": "Bootstrapped AI and tech products"
    },
    "BetaList": {
        "url": "https://betalist.com/feed",
        "tier": 2,
        "focus": "Early-stage AI startup launches"
    },
    "SaaS Weekly": {
        "url": "https://saasweekly.substack.com/feed",
        "tier": 2,
        "focus": "AI SaaS products and trends"
    },
    "There's An AI For That": {
        "url": "https://theresanaiforthat.com/rss/",
        "tier": 2,
        "focus": "AI tool discovery and reviews"
    },
    "AI Tool Guru": {
        "url": "https://aitoolguru.substack.com/feed",
        "tier": 2,
        "focus": "AI tool reviews and comparisons"
    },
    "Future Tools (Matt Wolfe)": {
        "url": "https://futuretools.beehiiv.com/feed",
        "tier": 2,
        "focus": "Weekly AI tool roundup"
    },
    "Futurepedia": {
        "url": "https://www.futurepedia.io/feed.xml",
        "tier": 2,
        "focus": "AI tools directory and news"
    },
    "Toolify AI": {
        "url": "https://www.toolify.ai/feed",
        "tier": 2,
        "focus": "AI tool aggregation and discovery"
    },
    "AI Scout": {
        "url": "https://aiscout.substack.com/feed",
        "tier": 2,
        "focus": "AI startup and tool scouting"
    },
    "Hacker Newsletter": {
        "url": "https://hackernewsletter.com/rss/",
        "tier": 2,
        "focus": "Curated best of Hacker News weekly"
    },
    "Changelog": {
        "url": "https://changelog.com/feed",
        "tier": 2,
        "focus": "Open source and developer tools news"
    },
    "Dev.to AI": {
        "url": "https://dev.to/feed/tag/ai",
        "tier": 2,
        "focus": "Developer community AI articles"
    },
    "Hacker Noon AI": {
        "url": "https://hackernoon.com/tagged/artificial-intelligence/feed",
        "tier": 2,
        "focus": "Developer-written AI articles"
    },
    "SaaStr Blog": {
        "url": "https://www.saastr.com/feed/",
        "tier": 2,
        "focus": "AI SaaS strategy and growth"
    },

    # =========================================================================
    # TIER 3: Weekly Depth — 100 sources
    # =========================================================================

    # --- Long-form AI Analysis (30) ---
    "One Useful Thing (Ethan Mollick)": {
        "url": "https://www.oneusefulthing.org/feed",
        "tier": 3,
        "focus": "AI implications, practical experiments"
    },
    "Turing Post": {
        "url": "https://www.turingpost.com/feed",
        "tier": 3,
        "focus": "AI/ML deep dives, agentic workflows, business"
    },
    "Chip Huyen": {
        "url": "https://huyenchip.com/feed",
        "tier": 3,
        "focus": "ML engineering, production systems, infrastructure"
    },
    "Stratechery (Ben Thompson)": {
        "url": "https://stratechery.com/feed/",
        "tier": 3,
        "focus": "Tech strategy, AI business implications"
    },
    "Not Boring (Packy McCormick)": {
        "url": "https://www.notboring.co/feed",
        "tier": 3,
        "focus": "AI business strategy, deep-dive company analysis"
    },
    "Lenny's Newsletter": {
        "url": "https://www.lennysnewsletter.com/feed",
        "tier": 3,
        "focus": "Product management and AI product strategy"
    },
    "Eugene Yan": {
        "url": "https://eugeneyan.com/rss/",
        "tier": 3,
        "focus": "ML systems design and applied ML"
    },
    "Lilian Weng (OpenAI)": {
        "url": "https://lilianweng.github.io/index.xml",
        "tier": 3,
        "focus": "Technical deep dives on ML concepts"
    },
    "Jay Alammar": {
        "url": "https://jalammar.github.io/feed.xml",
        "tier": 3,
        "focus": "Visual explanations of ML concepts"
    },
    "Andrej Karpathy Blog": {
        "url": "https://karpathy.github.io/feed.xml",
        "tier": 3,
        "focus": "Neural networks, training techniques, LLMs"
    },
    "The AI Edge (Damien Benveniste)": {
        "url": "https://newsletter.theaiedge.io/feed",
        "tier": 3,
        "focus": "ML system design for production"
    },
    "Elad Gil Blog": {
        "url": "https://blog.eladgil.com/feed",
        "tier": 3,
        "focus": "AI market analysis and founder advice"
    },
    "Benedict Evans": {
        "url": "https://www.ben-evans.com/feed",
        "tier": 3,
        "focus": "Tech and AI macro trend analysis"
    },
    "Matt Rickard": {
        "url": "https://matt-rickard.com/rss",
        "tier": 3,
        "focus": "AI infrastructure and developer tools"
    },
    "Swyx (shawn wang)": {
        "url": "https://www.latent.space/feed",
        "tier": 3,
        "focus": "AI engineering and the AI engineer stack"
    },
    "Cameron Wolfe": {
        "url": "https://cameronrwolfe.substack.com/feed",
        "tier": 3,
        "focus": "Deep learning research explained clearly"
    },
    "Gradient Flow": {
        "url": "https://gradientflow.com/feed/",
        "tier": 3,
        "focus": "AI/ML industry trends and analysis"
    },
    "Machine Learning Street Talk": {
        "url": "https://www.mlst.ai/feed",
        "tier": 3,
        "focus": "Deep technical ML discussions"
    },
    "The Pragmatic Engineer (AI)": {
        "url": "https://newsletter.pragmaticengineer.com/feed",
        "tier": 3,
        "focus": "AI's impact on software engineering"
    },
    "Gary Marcus (Road to AI We Can Trust)": {
        "url": "https://garymarcus.substack.com/feed",
        "tier": 3,
        "focus": "AI criticism, AGI skepticism, safety"
    },
    "Zvi Mowshowitz (Don't Worry About The Vase)": {
        "url": "https://thezvi.substack.com/feed",
        "tier": 3,
        "focus": "Exhaustive AI news analysis and commentary"
    },
    "Dan Shipper (Every)": {
        "url": "https://every.to/feed",
        "tier": 3,
        "focus": "AI for knowledge work and productivity"
    },
    "Brian Christian": {
        "url": "https://brianchristian.org/feed/",
        "tier": 3,
        "focus": "AI alignment and human implications"
    },
    "Wait But Why": {
        "url": "https://waitbutwhy.com/feed",
        "tier": 3,
        "focus": "Long-form AI and future of humanity"
    },
    "No Priors (podcast blog)": {
        "url": "https://www.nopriors.ai/feed",
        "tier": 3,
        "focus": "AI industry leader interviews"
    },
    "Astral Codex Ten (Scott Alexander)": {
        "url": "https://www.astralcodexten.com/feed",
        "tier": 3,
        "focus": "AI risk, prediction markets, rationalist analysis"
    },
    "Colossus / Invest Like the Best": {
        "url": "https://www.joincolossus.com/feed",
        "tier": 3,
        "focus": "AI business models and investing"
    },
    "Understanding AI": {
        "url": "https://www.understandingai.org/feed",
        "tier": 3,
        "focus": "Making AI research accessible"
    },
    "The Markup": {
        "url": "https://themarkup.org/feeds/rss.xml",
        "tier": 3,
        "focus": "AI accountability and investigative tech journalism"
    },
    "AI Alignment Forum": {
        "url": "https://www.alignmentforum.org/feed.xml",
        "tier": 3,
        "focus": "AI safety research and alignment"
    },

    # --- Academic/Research Blogs (30) ---
    "Distill.pub": {
        "url": "https://distill.pub/rss.xml",
        "tier": 3,
        "focus": "Interactive ML research visualization"
    },
    "Papers With Code": {
        "url": "https://paperswithcode.com/rss",
        "tier": 3,
        "focus": "Trending ML papers with implementations"
    },
    "Google Research Blog": {
        "url": "https://blog.research.google/feeds/posts/default?alt=rss",
        "tier": 3,
        "focus": "Google AI/ML research papers and breakthroughs"
    },
    "Microsoft Research Blog": {
        "url": "https://www.microsoft.com/en-us/research/feed/",
        "tier": 3,
        "focus": "MS AI research, tools, and systems"
    },
    "Meta AI Blog": {
        "url": "https://ai.meta.com/blog/rss/",
        "tier": 3,
        "focus": "LLaMA, open-source AI research"
    },
    "DeepMind Blog": {
        "url": "https://deepmind.google/blog/rss.xml",
        "tier": 3,
        "focus": "Frontier AI research and applications"
    },
    "NVIDIA AI Blog": {
        "url": "https://blogs.nvidia.com/feed/",
        "tier": 3,
        "focus": "GPU AI, inference, training infrastructure"
    },
    "Apple ML Research": {
        "url": "https://machinelearning.apple.com/rss.xml",
        "tier": 3,
        "focus": "On-device ML, privacy-preserving AI"
    },
    "Amazon Science": {
        "url": "https://www.amazon.science/index.rss",
        "tier": 3,
        "focus": "Applied AI research and Alexa/AWS ML"
    },
    "Salesforce AI Research": {
        "url": "https://blog.salesforceairesearch.com/rss/",
        "tier": 3,
        "focus": "Enterprise AI and NLP research"
    },
    "Stanford HAI": {
        "url": "https://hai.stanford.edu/news/rss.xml",
        "tier": 3,
        "focus": "Human-centered AI research and policy"
    },
    "MIT CSAIL": {
        "url": "https://www.csail.mit.edu/news/feed",
        "tier": 3,
        "focus": "MIT computer science and AI research"
    },
    "Berkeley AI Research (BAIR)": {
        "url": "https://bair.berkeley.edu/blog/feed.xml",
        "tier": 3,
        "focus": "Robotics, RL, vision, NLP research"
    },
    "Carnegie Mellon AI": {
        "url": "https://ai.cmu.edu/feed",
        "tier": 3,
        "focus": "CMU AI research and education"
    },
    "Allen Institute for AI (AI2)": {
        "url": "https://blog.allenai.org/feed",
        "tier": 3,
        "focus": "Open research: OLMo, Semantic Scholar"
    },
    "EleutherAI Blog": {
        "url": "https://blog.eleuther.ai/rss/",
        "tier": 3,
        "focus": "Open-source LLM research"
    },
    "Cohere For AI": {
        "url": "https://cohere.com/blog/rss",
        "tier": 3,
        "focus": "Multilingual NLP and research"
    },
    "Stability AI Blog": {
        "url": "https://stability.ai/blog/rss.xml",
        "tier": 3,
        "focus": "Image generation, open models"
    },
    "Together AI Blog": {
        "url": "https://www.together.ai/blog/rss",
        "tier": 3,
        "focus": "Open-source AI infrastructure"
    },
    "Mistral AI Blog": {
        "url": "https://mistral.ai/feed",
        "tier": 3,
        "focus": "European open-weight LLM research"
    },
    "arXiv CS.AI (recent)": {
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "tier": 3,
        "focus": "Latest AI papers from arXiv"
    },
    "arXiv CS.CL (NLP)": {
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "tier": 3,
        "focus": "Latest NLP/language model papers"
    },
    "arXiv CS.LG (Machine Learning)": {
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "tier": 3,
        "focus": "Latest machine learning papers"
    },
    "arXiv CS.CV (Computer Vision)": {
        "url": "https://rss.arxiv.org/rss/cs.CV",
        "tier": 3,
        "focus": "Latest computer vision papers"
    },
    "Semantic Scholar AI Feed": {
        "url": "https://www.semanticscholar.org/feed",
        "tier": 3,
        "focus": "AI-curated academic paper recommendations"
    },
    "Two Minute Papers (YouTube RSS)": {
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCbfYPyITQ-7l4upoX8nvctg",
        "tier": 3,
        "focus": "Visual AI research paper summaries"
    },
    "Yannic Kilcher (YouTube RSS)": {
        "url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCZHmQk67mSJgfCCTn7xBfew",
        "tier": 3,
        "focus": "In-depth ML paper explanations"
    },
    "The Gradient Pub": {
        "url": "https://thegradient.pub/rss/",
        "tier": 3,
        "focus": "Research perspectives from academics"
    },
    "Transformer Circuits (Anthropic)": {
        "url": "https://transformer-circuits.pub/rss.xml",
        "tier": 3,
        "focus": "Mechanistic interpretability research"
    },
    "OpenReview (ICLR/NeurIPS featured)": {
        "url": "https://openreview.net/rss",
        "tier": 3,
        "focus": "Top peer-reviewed ML conference papers"
    },

    # --- AI Strategy & Business (20) ---
    "McKinsey AI Insights": {
        "url": "https://www.mckinsey.com/capabilities/quantumblack/our-insights/rss",
        "tier": 3,
        "focus": "AI enterprise strategy and transformation"
    },
    "Deloitte AI Institute": {
        "url": "https://www2.deloitte.com/us/en/pages/deloitte-analytics/topics/ai-institute.html/feed",
        "tier": 3,
        "focus": "AI business adoption and governance"
    },
    "BCG AI": {
        "url": "https://www.bcg.com/publications/rss.xml",
        "tier": 3,
        "focus": "Responsible AI and enterprise strategy"
    },
    "Accenture AI Blog": {
        "url": "https://www.accenture.com/us-en/blogs/technology-innovation/rss",
        "tier": 3,
        "focus": "Enterprise AI transformation"
    },
    "Gartner Research (Tech)": {
        "url": "https://www.gartner.com/en/articles/rss",
        "tier": 3,
        "focus": "AI hype cycle, market predictions"
    },
    "Forrester AI Blog": {
        "url": "https://www.forrester.com/blogs/category/artificial-intelligence/feed/",
        "tier": 3,
        "focus": "AI market research and enterprise adoption"
    },
    "Harvard Business Review AI": {
        "url": "https://hbr.org/topic/technology/feed",
        "tier": 3,
        "focus": "AI leadership and business strategy"
    },
    "MIT Sloan Management Review": {
        "url": "https://sloanreview.mit.edu/feed/",
        "tier": 3,
        "focus": "AI management and organizational change"
    },
    "O'Reilly Radar": {
        "url": "https://www.oreilly.com/radar/feed/",
        "tier": 3,
        "focus": "Emerging tech trends and AI"
    },
    "InfoQ AI/ML": {
        "url": "https://feed.infoq.com/ai-ml-data-eng/",
        "tier": 3,
        "focus": "Enterprise AI architecture and engineering"
    },
    "AI Business": {
        "url": "https://aibusiness.com/rss.xml",
        "tier": 3,
        "focus": "Enterprise AI news and case studies"
    },
    "Data Robot Blog": {
        "url": "https://www.datarobot.com/blog/rss/",
        "tier": 3,
        "focus": "Enterprise ML platform and AutoML"
    },
    "Databricks Blog": {
        "url": "https://www.databricks.com/feed",
        "tier": 3,
        "focus": "Data+AI, lakehouse, ML workflows"
    },
    "Snowflake Blog": {
        "url": "https://www.snowflake.com/feed/",
        "tier": 3,
        "focus": "AI data cloud and analytics"
    },
    "Scale AI Blog": {
        "url": "https://scale.com/blog/rss",
        "tier": 3,
        "focus": "Data labeling, AI infrastructure at scale"
    },
    "Anyscale Blog": {
        "url": "https://www.anyscale.com/blog/rss",
        "tier": 3,
        "focus": "Ray, distributed AI, LLM serving"
    },
    "Modal Blog": {
        "url": "https://modal.com/blog/feed.xml",
        "tier": 3,
        "focus": "Serverless AI infrastructure"
    },
    "Replicate Blog": {
        "url": "https://replicate.com/blog/rss",
        "tier": 3,
        "focus": "Running open-source AI models"
    },
    "Weights & Biases (Fully Connected)": {
        "url": "https://wandb.ai/fully-connected/rss.xml",
        "tier": 3,
        "focus": "MLOps deep dives and tutorials"
    },
    "AI Infrastructure Alliance": {
        "url": "https://ai-infrastructure.org/feed/",
        "tier": 3,
        "focus": "AI infrastructure ecosystem and standards"
    },

    # --- Podcast RSS Feeds (20) ---
    "Latent Space Podcast": {
        "url": "https://api.substack.com/feed/podcast/1084089.rss",
        "tier": 3,
        "focus": "AI engineering interviews and deep dives"
    },
    "Practical AI (Changelog)": {
        "url": "https://changelog.com/practicalai/feed",
        "tier": 3,
        "focus": "Making AI practical and accessible"
    },
    "TWIML AI Podcast": {
        "url": "https://twimlai.com/feed/",
        "tier": 3,
        "focus": "ML and AI interviews with researchers"
    },
    "Gradient Dissent (W&B)": {
        "url": "https://feeds.soundcloud.com/users/soundcloud:users:656256180/sounds.rss",
        "tier": 3,
        "focus": "ML practitioners sharing experiences"
    },
    "Lex Fridman Podcast": {
        "url": "https://lexfridman.com/feed/podcast/",
        "tier": 3,
        "focus": "Long-form AI researcher interviews"
    },
    "The Cognitive Revolution": {
        "url": "https://www.cognitiverevolution.ai/feed",
        "tier": 3,
        "focus": "AI impact on society and business"
    },
    "Eye on AI": {
        "url": "https://www.eye-on.ai/podcast-feed.xml",
        "tier": 3,
        "focus": "AI industry interview series"
    },
    "AI Podcast (NVIDIA)": {
        "url": "https://feeds.soundcloud.com/users/soundcloud:users:264034133/sounds.rss",
        "tier": 3,
        "focus": "NVIDIA AI research and applications"
    },
    "No Priors Podcast": {
        "url": "https://feeds.transistor.fm/no-priors",
        "tier": 3,
        "focus": "a16z AI industry interviews"
    },
    "Hard Fork (NYT)": {
        "url": "https://feeds.simplecast.com/l2i9YnTd",
        "tier": 3,
        "focus": "Tech and AI culture, weekly"
    },
    "The AI Breakdown": {
        "url": "https://feeds.libsyn.com/467852/rss",
        "tier": 3,
        "focus": "Daily AI news analysis"
    },
    "Last Week in AI Podcast": {
        "url": "https://feeds.buzzsprout.com/2004244.rss",
        "tier": 3,
        "focus": "Weekly AI news discussion"
    },
    "80,000 Hours Podcast": {
        "url": "https://feeds.feedburner.com/80000HoursPodcast",
        "tier": 3,
        "focus": "AI safety and existential risk"
    },
    "Machine Learning Guide": {
        "url": "https://feeds.megaphone.fm/MLG6457688850",
        "tier": 3,
        "focus": "ML fundamentals education"
    },
    "Data Skeptic": {
        "url": "https://dataskeptic.libsyn.com/rss",
        "tier": 3,
        "focus": "Data science and ML topics"
    },
    "Talking Machines": {
        "url": "https://www.thetalkingmachines.com/feed.xml",
        "tier": 3,
        "focus": "Academic ML research discussions"
    },
    "The Robot Brains (Pieter Abbeel)": {
        "url": "https://feeds.simplecast.com/gdzDyg_X",
        "tier": 3,
        "focus": "Robotics and AI research frontiers"
    },
    "Dwarkesh Podcast": {
        "url": "https://feeds.megaphone.fm/dwarkeshpatel",
        "tier": 3,
        "focus": "Deep interviews on AI and progress"
    },
    "Generally Intelligent": {
        "url": "https://generallyintelligent.com/podcast/rss",
        "tier": 3,
        "focus": "AI research and safety"
    },
    "The Inside View": {
        "url": "https://theinsideview.ai/feed",
        "tier": 3,
        "focus": "AI governance and safety interviews"
    },

    # =========================================================================
    # TIER 4: Community Signal — 100 sources
    # =========================================================================

    # --- Reddit RSS Feeds (20) ---
    "r/MachineLearning": {
        "url": "https://www.reddit.com/r/MachineLearning/.rss",
        "tier": 4,
        "focus": "ML research discussion and papers"
    },
    "r/artificial": {
        "url": "https://www.reddit.com/r/artificial/.rss",
        "tier": 4,
        "focus": "General AI news and discussion"
    },
    "r/AI_Agents": {
        "url": "https://www.reddit.com/r/AI_Agents/.rss",
        "tier": 4,
        "focus": "AI agent development and frameworks"
    },
    "r/LocalLLaMA": {
        "url": "https://www.reddit.com/r/LocalLLaMA/.rss",
        "tier": 4,
        "focus": "Running LLMs locally, open models"
    },
    "r/LangChain": {
        "url": "https://www.reddit.com/r/LangChain/.rss",
        "tier": 4,
        "focus": "LangChain framework discussion"
    },
    "r/ClaudeAI": {
        "url": "https://www.reddit.com/r/ClaudeAI/.rss",
        "tier": 4,
        "focus": "Claude usage, tips, and discussion"
    },
    "r/ChatGPT": {
        "url": "https://www.reddit.com/r/ChatGPT/.rss",
        "tier": 4,
        "focus": "ChatGPT usage and community"
    },
    "r/OpenAI": {
        "url": "https://www.reddit.com/r/OpenAI/.rss",
        "tier": 4,
        "focus": "OpenAI news and products"
    },
    "r/StableDiffusion": {
        "url": "https://www.reddit.com/r/StableDiffusion/.rss",
        "tier": 4,
        "focus": "Image generation and diffusion models"
    },
    "r/MLOps": {
        "url": "https://www.reddit.com/r/mlops/.rss",
        "tier": 4,
        "focus": "ML operations and deployment"
    },
    "r/deeplearning": {
        "url": "https://www.reddit.com/r/deeplearning/.rss",
        "tier": 4,
        "focus": "Deep learning research and practice"
    },
    "r/LanguageTechnology": {
        "url": "https://www.reddit.com/r/LanguageTechnology/.rss",
        "tier": 4,
        "focus": "NLP and computational linguistics"
    },
    "r/learnmachinelearning": {
        "url": "https://www.reddit.com/r/learnmachinelearning/.rss",
        "tier": 4,
        "focus": "ML learning resources and questions"
    },
    "r/singularity": {
        "url": "https://www.reddit.com/r/singularity/.rss",
        "tier": 4,
        "focus": "AGI speculation and AI progress"
    },
    "r/ArtificialIntelligence": {
        "url": "https://www.reddit.com/r/ArtificialIntelligence/.rss",
        "tier": 4,
        "focus": "AI news and beginner discussion"
    },
    "r/PromptEngineering": {
        "url": "https://www.reddit.com/r/PromptEngineering/.rss",
        "tier": 4,
        "focus": "Prompt design and optimization"
    },
    "r/AutoGen": {
        "url": "https://www.reddit.com/r/AutoGen/.rss",
        "tier": 4,
        "focus": "Microsoft AutoGen multi-agent framework"
    },
    "r/ollama": {
        "url": "https://www.reddit.com/r/ollama/.rss",
        "tier": 4,
        "focus": "Running Ollama local LLMs"
    },
    "r/Bard": {
        "url": "https://www.reddit.com/r/Bard/.rss",
        "tier": 4,
        "focus": "Google Gemini/Bard usage"
    },
    "r/mlscaling": {
        "url": "https://www.reddit.com/r/mlscaling/.rss",
        "tier": 4,
        "focus": "ML scaling laws and research"
    },

    # --- Hacker News Filtered Feeds (10) ---
    "Hacker News (Front Page)": {
        "url": "https://hnrss.org/frontpage",
        "tier": 4,
        "focus": "Tech community signal, early trends"
    },
    "HN Best Stories": {
        "url": "https://hnrss.org/best",
        "tier": 4,
        "focus": "Highest-ranked HN stories"
    },
    "HN: AI keyword": {
        "url": "https://hnrss.org/newest?q=artificial+intelligence",
        "tier": 4,
        "focus": "HN posts mentioning AI"
    },
    "HN: LLM keyword": {
        "url": "https://hnrss.org/newest?q=LLM",
        "tier": 4,
        "focus": "HN posts about large language models"
    },
    "HN: GPT keyword": {
        "url": "https://hnrss.org/newest?q=GPT",
        "tier": 4,
        "focus": "HN posts about GPT models"
    },
    "HN: Machine Learning": {
        "url": "https://hnrss.org/newest?q=machine+learning",
        "tier": 4,
        "focus": "HN posts about machine learning"
    },
    "HN: AI Agents": {
        "url": "https://hnrss.org/newest?q=AI+agents",
        "tier": 4,
        "focus": "HN posts about AI agents"
    },
    "HN: Claude": {
        "url": "https://hnrss.org/newest?q=Claude+Anthropic",
        "tier": 4,
        "focus": "HN posts about Claude and Anthropic"
    },
    "HN: Open Source AI": {
        "url": "https://hnrss.org/newest?q=open+source+AI",
        "tier": 4,
        "focus": "HN posts about open-source AI"
    },
    "HN: Show HN AI": {
        "url": "https://hnrss.org/show?q=AI",
        "tier": 4,
        "focus": "Show HN posts related to AI"
    },

    # --- Discord/Community RSS & Changelogs (10) ---
    "OpenAI Changelog": {
        "url": "https://openai.com/changelog/rss.xml",
        "tier": 4,
        "focus": "OpenAI API and product updates"
    },
    "Anthropic News": {
        "url": "https://www.anthropic.com/feed",
        "tier": 4,
        "focus": "Claude updates and releases"
    },
    "LangChain Changelog": {
        "url": "https://changelog.langchain.com/feed",
        "tier": 4,
        "focus": "LangChain framework updates"
    },
    "LlamaIndex Blog": {
        "url": "https://www.llamaindex.ai/blog/rss.xml",
        "tier": 4,
        "focus": "RAG framework updates and tutorials"
    },
    "CrewAI Blog": {
        "url": "https://www.crewai.com/blog/feed",
        "tier": 4,
        "focus": "Multi-agent framework updates"
    },
    "Vercel AI Blog": {
        "url": "https://vercel.com/blog/feed.xml",
        "tier": 4,
        "focus": "AI SDK, Next.js AI integration"
    },
    "Supabase Blog": {
        "url": "https://supabase.com/blog/rss.xml",
        "tier": 4,
        "focus": "AI vector search and pgvector"
    },
    "Pinecone Blog": {
        "url": "https://www.pinecone.io/blog/rss.xml",
        "tier": 4,
        "focus": "Vector database and RAG patterns"
    },
    "Weaviate Blog": {
        "url": "https://weaviate.io/blog/feed.xml",
        "tier": 4,
        "focus": "Vector search and AI applications"
    },
    "Qdrant Blog": {
        "url": "https://qdrant.tech/blog/feed.xml",
        "tier": 4,
        "focus": "Vector similarity search engine"
    },

    # --- GitHub Trending & Release Feeds (10) ---
    "GitHub Trending (all)": {
        "url": "https://rsshub.app/github/trending/daily",
        "tier": 4,
        "focus": "Daily trending GitHub repositories"
    },
    "GitHub Trending Python": {
        "url": "https://rsshub.app/github/trending/daily/python",
        "tier": 4,
        "focus": "Trending Python AI/ML repos"
    },
    "GitHub Trending Jupyter": {
        "url": "https://rsshub.app/github/trending/daily/jupyter-notebook",
        "tier": 4,
        "focus": "Trending ML notebooks"
    },
    "GitHub: langchain releases": {
        "url": "https://github.com/langchain-ai/langchain/releases.atom",
        "tier": 4,
        "focus": "LangChain release notes"
    },
    "GitHub: llama.cpp releases": {
        "url": "https://github.com/ggerganov/llama.cpp/releases.atom",
        "tier": 4,
        "focus": "Local LLM inference updates"
    },
    "GitHub: vllm releases": {
        "url": "https://github.com/vllm-project/vllm/releases.atom",
        "tier": 4,
        "focus": "LLM serving engine updates"
    },
    "GitHub: transformers releases": {
        "url": "https://github.com/huggingface/transformers/releases.atom",
        "tier": 4,
        "focus": "HuggingFace Transformers updates"
    },
    "GitHub: ollama releases": {
        "url": "https://github.com/ollama/ollama/releases.atom",
        "tier": 4,
        "focus": "Ollama local LLM runner"
    },
    "GitHub: open-webui releases": {
        "url": "https://github.com/open-webui/open-webui/releases.atom",
        "tier": 4,
        "focus": "Open WebUI for local LLMs"
    },
    "GitHub: dify releases": {
        "url": "https://github.com/langgenius/dify/releases.atom",
        "tier": 4,
        "focus": "Dify LLM app development platform"
    },

    # --- General Tech News (20) ---
    "Ars Technica AI": {
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "tier": 4,
        "focus": "Deep technical analysis, security, research"
    },
    "MIT Technology Review AI": {
        "url": "https://www.technologyreview.com/feed/",
        "tier": 4,
        "focus": "Research, policy, long-range implications"
    },
    "IEEE Spectrum AI": {
        "url": "https://spectrum.ieee.org/feeds/topic/artificial-intelligence.rss",
        "tier": 4,
        "focus": "Engineering and technical AI advances"
    },
    "Nature Machine Intelligence": {
        "url": "https://www.nature.com/natmachintell.rss",
        "tier": 4,
        "focus": "Peer-reviewed AI research"
    },
    "Science (AAAS) AI": {
        "url": "https://www.science.org/action/showFeed?type=searchTopic&value=artificial-intelligence&uri=/topic/ai",
        "tier": 4,
        "focus": "Scientific AI breakthroughs"
    },
    "New Scientist AI": {
        "url": "https://www.newscientist.com/subject/technology/feed/",
        "tier": 4,
        "focus": "AI science reporting"
    },
    "Quanta Magazine (CS)": {
        "url": "https://api.quantamagazine.org/feed/",
        "tier": 4,
        "focus": "Deep science and math behind AI"
    },
    "Scientific American AI": {
        "url": "https://rss.sciam.com/ScientificAmerican-Global",
        "tier": 4,
        "focus": "AI science for general audiences"
    },
    "Slashdot AI": {
        "url": "https://rss.slashdot.org/Slashdot/slashdotMain",
        "tier": 4,
        "focus": "Tech community news aggregation"
    },
    "Lobsters": {
        "url": "https://lobste.rs/rss",
        "tier": 4,
        "focus": "Technical programming and AI links"
    },
    "The Conversation AI": {
        "url": "https://theconversation.com/us/technology/articles.atom",
        "tier": 4,
        "focus": "Academic experts explain AI topics"
    },
    "ACM TechNews": {
        "url": "https://technews.acm.org/rss.xml",
        "tier": 4,
        "focus": "Computing and AI news from ACM"
    },
    "Communications of the ACM": {
        "url": "https://cacm.acm.org/feed/",
        "tier": 4,
        "focus": "Computing research and practice"
    },
    "The Economist Technology": {
        "url": "https://www.economist.com/science-and-technology/rss.xml",
        "tier": 4,
        "focus": "Global tech and AI economic analysis"
    },
    "Turing Institute Blog": {
        "url": "https://www.turing.ac.uk/blog/feed",
        "tier": 4,
        "focus": "UK national AI research institute"
    },
    "DeepTech (by The Logic)": {
        "url": "https://deeptech.substack.com/feed",
        "tier": 4,
        "focus": "Deep technology industry analysis"
    },
    "Sifted (EU Tech)": {
        "url": "https://sifted.eu/feed",
        "tier": 4,
        "focus": "European tech and AI startups"
    },
    "Tech.eu": {
        "url": "https://tech.eu/feed/",
        "tier": 4,
        "focus": "European technology news"
    },
    "ReadWrite AI": {
        "url": "https://readwrite.com/category/ai/feed/",
        "tier": 4,
        "focus": "AI industry news and analysis"
    },
    "Unite.AI": {
        "url": "https://www.unite.ai/feed/",
        "tier": 4,
        "focus": "AI news, reviews, and interviews"
    },

    # --- International Sources (15) ---
    "Nikkei Asia Tech": {
        "url": "https://asia.nikkei.com/rss/feed/Technology",
        "tier": 4,
        "focus": "Asian AI industry and policy"
    },
    "South China Morning Post Tech": {
        "url": "https://www.scmp.com/rss/5/feed",
        "tier": 4,
        "focus": "China AI developments"
    },
    "TechNode (China AI)": {
        "url": "https://technode.com/feed/",
        "tier": 4,
        "focus": "Chinese tech and AI startups"
    },
    "KrASIA": {
        "url": "https://kr-asia.com/feed",
        "tier": 4,
        "focus": "Southeast Asian tech and AI"
    },
    "Tech in Asia": {
        "url": "https://www.techinasia.com/feed",
        "tier": 4,
        "focus": "Asian startup and AI ecosystem"
    },
    "The Ken (India)": {
        "url": "https://the-ken.com/feed/",
        "tier": 4,
        "focus": "Indian tech and AI industry"
    },
    "ET Tech (India)": {
        "url": "https://economictimes.indiatimes.com/tech/rssfeeds/13357270.cms",
        "tier": 4,
        "focus": "Indian tech sector and AI"
    },
    "ZDNET Japan AI (English)": {
        "url": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "tier": 4,
        "focus": "Global AI enterprise coverage"
    },
    "Synced Review (China AI)": {
        "url": "https://syncedreview.com/feed/",
        "tier": 4,
        "focus": "Chinese AI research and industry"
    },
    "EU AI Alliance Blog": {
        "url": "https://futurium.ec.europa.eu/en/european-ai-alliance/rss.xml",
        "tier": 4,
        "focus": "EU AI community discussion"
    },
    "Tencent AI Lab Blog": {
        "url": "https://ai.tencent.com/ailab/en/feed",
        "tier": 4,
        "focus": "Tencent AI research"
    },
    "Samsung AI Research": {
        "url": "https://research.samsung.com/feed",
        "tier": 4,
        "focus": "Samsung on-device AI research"
    },
    "Toyota Research Institute": {
        "url": "https://www.tri.global/feed",
        "tier": 4,
        "focus": "Robotics and autonomous AI"
    },
    "Alan Turing Institute News": {
        "url": "https://www.turing.ac.uk/news/feed",
        "tier": 4,
        "focus": "UK AI research and national strategy"
    },
    "Montreal AI Ethics Institute": {
        "url": "https://montrealethics.ai/feed/",
        "tier": 4,
        "focus": "AI ethics research, global perspective"
    },

    # --- Government/Policy (15) ---
    "NIST AI": {
        "url": "https://www.nist.gov/artificial-intelligence/rss.xml",
        "tier": 4,
        "focus": "US AI standards and risk framework"
    },
    "White House OSTP": {
        "url": "https://www.whitehouse.gov/ostp/feed/",
        "tier": 4,
        "focus": "US science and technology policy"
    },
    "EU AI Act News": {
        "url": "https://artificialintelligenceact.eu/feed/",
        "tier": 4,
        "focus": "EU AI regulation updates"
    },
    "UK AI Safety Institute": {
        "url": "https://www.aisi.gov.uk/feed",
        "tier": 4,
        "focus": "UK AI safety evaluations and policy"
    },
    "FTC Tech Blog": {
        "url": "https://www.ftc.gov/policy/advocacy-research/tech-at-ftc/rss.xml",
        "tier": 4,
        "focus": "US AI regulation and consumer protection"
    },
    "OECD AI Policy Observatory": {
        "url": "https://oecd.ai/en/feed",
        "tier": 4,
        "focus": "International AI policy coordination"
    },
    "UNESCO AI Ethics": {
        "url": "https://www.unesco.org/en/artificial-intelligence/rss",
        "tier": 4,
        "focus": "Global AI ethics framework"
    },
    "Center for AI Safety": {
        "url": "https://www.safe.ai/feed",
        "tier": 4,
        "focus": "AI catastrophic risk and safety"
    },
    "Partnership on AI": {
        "url": "https://partnershiponai.org/feed/",
        "tier": 4,
        "focus": "Responsible AI practices"
    },
    "Future of Life Institute": {
        "url": "https://futureoflife.org/feed/",
        "tier": 4,
        "focus": "Existential AI risk and governance"
    },
    "Center for AI and Digital Policy": {
        "url": "https://www.caidp.org/feed/",
        "tier": 4,
        "focus": "AI policy research and advocacy"
    },
    "Brookings AI": {
        "url": "https://www.brookings.edu/topic/artificial-intelligence/feed/",
        "tier": 4,
        "focus": "AI policy research and analysis"
    },
    "RAND AI": {
        "url": "https://www.rand.org/topics/artificial-intelligence.xml",
        "tier": 4,
        "focus": "AI defense and policy research"
    },
    "Electronic Frontier Foundation AI": {
        "url": "https://www.eff.org/rss/updates.xml",
        "tier": 4,
        "focus": "Digital rights and AI civil liberties"
    },
    "AI Now Institute": {
        "url": "https://ainowinstitute.org/feed",
        "tier": 4,
        "focus": "Social implications of AI"
    },
}

MAX_ARTICLES_PER_FEED = 10


def fetch_articles(lookback_hours: int = 24) -> list[Article]:
    """
    Pull articles from all feeds published within the lookback window.

    Args:
        lookback_hours: How many hours back to look for articles

    Returns:
        List of Article objects
    """
    cutoff = datetime.now() - timedelta(hours=lookback_hours)
    all_articles = []

    for source_name, config in FEEDS.items():
        try:
            feed = feedparser.parse(config["url"])
            count = 0
            for entry in feed.entries:
                if count >= MAX_ARTICLES_PER_FEED:
                    break

                # Parse published date
                published = None
                for date_field in ["published_parsed", "updated_parsed"]:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        published = datetime(*getattr(entry, date_field)[:6])
                        break

                if not published:
                    # Try string parsing as fallback
                    for date_str_field in ["published", "updated"]:
                        if hasattr(entry, date_str_field):
                            try:
                                published = dateparser.parse(getattr(entry, date_str_field))
                                if published and published.tzinfo:
                                    published = published.replace(tzinfo=None)
                            except:
                                pass
                            break

                # If we still can't parse the date, include it anyway
                # (some feeds have unreliable dates)
                if published and published < cutoff:
                    continue

                title = entry.get("title", "Untitled")
                link = entry.get("link", "")
                summary = entry.get("summary", "")[:500]

                article = Article(
                    source=source_name,
                    tier=config["tier"],
                    title=title,
                    link=link,
                    summary=summary,
                    published=published.isoformat() if published else "unknown",
                    fetched_at=datetime.now().isoformat(),
                )
                all_articles.append(article)
                count += 1

        except Exception as e:
            print(f"  [WARN] Failed to fetch {source_name}: {e}")

    print(f"\n  Fetched {len(all_articles)} articles from {len(FEEDS)} sources.")
    return all_articles
