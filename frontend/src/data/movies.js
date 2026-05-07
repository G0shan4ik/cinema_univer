export const movies = [
  {
    id: 'dune-2',
    title: 'Dune: Part Two',
    genre: 'Sci-Fi',
    duration: '166 мин',
    age: '12+',
    rating: 8.7,
    premiere: 'Идет в прокате',
    description: 'Пол Атрейдес объединяется с фременами, чтобы вступить в решающую битву за Арракис.',
    highlight: 'IMAX, Dolby Atmos',
    poster: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=900&q=80'
  },
  {
    id: 'challengers',
    title: 'Challengers',
    genre: 'Drama',
    duration: '131 мин',
    age: '16+',
    rating: 7.8,
    premiere: 'Новинка недели',
    description: 'История о соперничестве, любви и спортивных амбициях на фоне большого тенниса.',
    highlight: 'Премьера, Lounge seats',
    poster: 'https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?auto=format&fit=crop&w=900&q=80'
  },
  {
    id: 'furiosa',
    title: 'Furiosa',
    genre: 'Action',
    duration: '148 мин',
    age: '18+',
    rating: 8.1,
    premiere: 'Скоро в кино',
    description: 'Приквел о становлении Фуриосы в суровом мире постапокалипсиса.',
    highlight: '4DX, Pre-sale',
    poster: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?auto=format&fit=crop&w=900&q=80'
  },
  {
    id: 'inside-out-2',
    title: 'Inside Out 2',
    genre: 'Animation',
    duration: '103 мин',
    age: '6+',
    rating: 8.4,
    premiere: 'Семейный хит',
    description: 'Новые эмоции приходят в команду Райли и превращают подростковую жизнь в приключение.',
    highlight: 'Kids hall, Family combo',
    poster: 'https://images.unsplash.com/photo-1514306191717-452ec28c7814?auto=format&fit=crop&w=900&q=80'
  }
]

export const favoriteMovieIds = ['dune-2', 'inside-out-2']

export const tickets = [
  {
    id: 1,
    movieId: 'dune-2',
    hall: 'Зал 1',
    seats: 'F5, F6',
    date: '10 апреля, 19:30'
  },
  {
    id: 2,
    movieId: 'challengers',
    hall: 'VIP Lounge',
    seats: 'B2',
    date: '12 апреля, 21:00'
  }
]

export const dashboardStats = [
  { label: 'Активные сеансы', value: '28' },
  { label: 'Продано билетов сегодня', value: '1 248' },
  { label: 'Конверсия бронирования', value: '7.2%' }
]
