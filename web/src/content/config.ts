import { defineCollection, z } from 'astro:content';

const digests = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    layout: z.string().optional(),
    draft: z.boolean().optional(),
  }),
});

const premium = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.string(),
    tier: z.enum(['free', 'pro', 'founding']),
    category: z.string(),
    layout: z.string().optional(),
    featured_free: z.boolean().optional(),
    draft: z.boolean().optional(),
  }),
});

export const collections = {
  digests,
  premium,
};
