import { apiPost } from './client'
import type { TokenResponse } from '../types'

export async function signup(username: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>('/auth/signup', { username, password })
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  return apiPost<TokenResponse>('/auth/login', { username, password })
}

export async function logout(): Promise<void> {
  return apiPost<void>('/auth/logout')
}
