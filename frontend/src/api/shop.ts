import type { BuyResponse, ShopItem } from '../types'

export async function listShop(): Promise<ShopItem[]> {
  // GET /shop
  throw new Error('not implemented')
}

export async function listInventory(): Promise<ShopItem[]> {
  // GET /shop/inventory
  throw new Error('not implemented')
}

export async function buyItem(_id: string): Promise<BuyResponse> {
  // POST /shop/{id}/buy
  throw new Error('not implemented')
}
