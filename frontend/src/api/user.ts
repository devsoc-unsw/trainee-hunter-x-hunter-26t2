import type { Me } from '../types'

export async function getMe(): Promise<Me> {
  // GET /users/me
  throw new Error('not implemented')
}

export async function updateUsername(_username: string): Promise<Me> {
  // PATCH /users/me
  throw new Error('not implemented')
}
