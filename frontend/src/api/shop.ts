import type { BuyResponse, ShopItem } from '../types'
import { apiGet, apiPost } from './client'

export async function listShop(): Promise<ShopItem[]> {
  // GET /shop
  return apiGet<ShopItem[]>('/shop')
}

export async function listInventory(): Promise<ShopItem[]> {
  // GET /shop/inventory
  return apiGet<ShopItem[]>('/shop/inventory')
}

export async function buyItem(id: string): Promise<BuyResponse> {
  // POST /shop/{id}/buy
  return apiPost<BuyResponse>(`/shop/${id}/buy`)
}
