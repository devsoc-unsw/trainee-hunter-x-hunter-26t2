// mirrors backend/models.py. if you change a model there, change it here too

export interface TokenResponse {
  token: string
}

export interface Me {
  id: string
  username: string
  coins: number
  solved_count: number
  unlocked_keys: number
}

export interface TestCase {
  input: unknown[]
  expected: unknown
}

export interface QuestionSummary {
  id: string
  slug: string
  name: string
  difficulty: 'easy' | 'medium' | 'hard'
  solved: boolean
}

export interface QuestionDetail {
  id: string
  slug: string
  name: string
  details: string
  difficulty: 'easy' | 'medium' | 'hard'
  function_name: string
  starter_code: string
  samples: TestCase[]
  solved: boolean
}

export interface TestResult {
  passed: boolean
  input: unknown[]
  expected: unknown
  got: unknown
  error: string | null
}

export interface SubmitResponse {
  passed: boolean
  results: TestResult[]
  coins_earned: number
  first_solve: boolean
}

export interface ShopItem {
  id: string
  name: string
  price: number
  image_url: string
  owned: boolean
}

export interface BuyResponse {
  item_id: string
  coins_left: number
}
