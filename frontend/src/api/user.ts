import type { Me } from '../types'
import { apiGet, apiPatch } from './client'

export async function getMe(): Promise<Me> {
  // GET /users/me
  // throw new Error('not implemented')
  return apiGet<Me>('/users/me')
}

export async function updateUsername(username: string): Promise<Me> {
  // PATCH /users/me
  return apiPatch<Me>('/users/me', { username })
}
