import { defineCollection, z } from 'astro:content';

const digests = defineCollection({
  type: 'content',
  schema: z.object({
    title: z.string(),
    date: z.string(),
    layout: z.string().optional(),
  }),
});

export const collections = {
  digests,
};
