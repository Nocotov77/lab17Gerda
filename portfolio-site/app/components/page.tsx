import ProjectCard from '../components/ProjectCard'

// TODO: Создайте массив с данными о проектах
const projects = [
  {
    title: 'Интернет-магазин',
    description: 'Полнофункциональный интернет-магазин с корзиной и оплатой',
    technologies: ['Next.js', 'TypeScript', 'Stripe'],
    link: 'https://example.com'
  },
  // TODO: Добавьте еще минимум 2 проекта
]

export default function ProjectsPage() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Мои проекты</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* TODO: Используйте компонент ProjectCard для отображения проектов */}
      </div>
    </div>
  )
}