export default function Shop() {
  // TODO: listShop() on mount, render a card per item with name + price,
  // a buy button that calls buyItem(id) then refresh() from useAuth so the
  // coin count updates. owned items show as owned instead of a button.
  // remember buy can fail: 402 = too poor, show the error nicely
  return (
    <div className="page">
      <h1>shop</h1>
      <p>shop items go here</p>
    </div>
  )
}
