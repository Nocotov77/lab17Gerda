export interface BlogPost {
  id: number
  title: string
  slug: string
  excerpt: string
  content: string
  date: string
  author: string
}

export const blogPosts: BlogPost[] = [
  {
    id: 1,
    title: 'Введение в Next.js',
    slug: 'introduction-to-nextjs',
    excerpt: 'Основы Next.js и преимущества серверного рендеринга',
    content: 'Полный текст статьи о Next.js...',
    date: '2026-01-15',
    author: 'Иван Иванов'
  },
  // TODO: Добавьте еще минимум 2 статьи самостоятельно
]