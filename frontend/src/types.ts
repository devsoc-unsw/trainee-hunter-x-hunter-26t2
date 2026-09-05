// mirrors backend/models.py. if you change a model there, change it here too

export interface TokenResponse {
  token: string
}

export interface Me {
  id: string
  username: string
  coins: number
  solved_count: number
  // WHICH keys are unlocked, not how many - the user picks each one
  unlocked_keys: string[]
  // unlocks earned but not yet placed. solving and buying both add to this;
  // clicking a locked key spends one
  unlock_credits: number
}

export interface TestCase {
  input: unknown[]
  expected: unknown
  is_sample?: boolean
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
  // true when the backend blanked input/expected/got because this is a hidden
  // test case. draw these as a bare 'Test 7 (hidden)' row - the fields are
  // empty, not missing
  hidden: boolean
}

export interface SubmitResponse {
  passed: boolean
  results: TestResult[]
  coins_earned: number
  first_solve: boolean
}

// what the Run button gets back. no coins_earned/first_solve - a run doesn't
// touch the database
export interface RunResponse {
  passed: boolean
  results: TestResult[]
}

export interface ShopItem {
  id: string
  // stable name for the item, eg 'blue-tulip'. map this to an imported png -
  // vite content-hashes src/assets, so image_url from the api can't be used
  // as a src directly
  slug: string
  name: string
  price: number
  image_url: string
  kind: 'key_skin' | 'accessory' | 'key_unlock'
  // an accessory only goes on a key of the same habitat: fish on water keys,
  // flowers and veg on the rest
  habitat: 'land' | 'water'
  // owns at least one
  owned: boolean
  // how many were bought, and how many of those are already on a key.
  // quantity - placed is what's left to plant.
  quantity: number
  placed: number
}

// how one key is dressed. keys the user hasn't touched aren't in the list -
// draw those as the default grass key with nothing on it.
export interface KeyDecor {
  key_char: string
  skin_slug: string | null
  accessory_slug: string | null
}

export interface BuyResponse {
  item_id: string
  coins_left: number
  // how many of it the user now owns. 0 for a key unlock, which becomes an
  // unlock credit rather than an inventory item.
  quantity: number
}

export interface UnlockResponse {
  key_char: string
  unlocked_keys: string[]
  unlock_credits: number
}

// how many copies of an item are still free to put on a key
export function unplaced(item: ShopItem): number {
  return item.quantity - item.placed
}
