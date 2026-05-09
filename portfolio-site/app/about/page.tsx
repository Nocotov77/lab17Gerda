export default function AboutPage() {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">Обо мне</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
        <h2 className="text-xl font-semibold mb-3">Навыки</h2>
        <ul className="list-disc pl-5 space-y-1">
          {/* TODO: Добавьте минимум 5 своих навыков */}
        </ul>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-3">Опыт работы</h2>
        <div className="space-y-4">
          {/* TODO: Добавьте минимум 2 пункта опыта работы */}
        </div>
      </div>
    </div>
  )
}