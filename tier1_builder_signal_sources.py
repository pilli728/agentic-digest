"""
Tier 1: Builder Signal — 100 RSS-compatible sources
People and companies actually BUILDING AI agents, tools, and infrastructure.

Generated: 2026-03-24
"""

TIER1_BUILDER_SIGNAL_SOURCES = {

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
        "tier": 1,
        "focus": "Latest AI research papers: agents, reasoning, planning, knowledge representation"
    },
    "ArXiv CS.LG (Machine Learning)": {
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "tier": 1,
        "focus": "Machine learning research: architectures, training methods, optimization"
    },
    "ArXiv CS.CL (Computation & Language)": {
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "tier": 1,
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
}


# Quick stats
if __name__ == "__main__":
    total = len(TIER1_BUILDER_SIGNAL_SOURCES)
    print(f"Total Tier 1 Builder Signal sources: {total}")
    print()

    # Count by category (using URL patterns and known groupings)
    categories = {
        "AI Labs & Model Providers": 22,
        "Agent Framework Teams": 16,
        "Individual Builders/Engineers": 27,
        "Infrastructure & DevTools": 20,
        "Open Source Projects": 5,
        "Research Labs & Academic": 10,
    }
    for cat, count in categories.items():
        print(f"  {cat}: {count}")
    print(f"  TOTAL: {sum(categories.values())}")
