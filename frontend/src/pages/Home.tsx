import { Link } from 'react-router-dom';

export default function Home() {
    return (
    <div className="m-6 flex flex-row">
        {/* im gonna need a header here but thats an issue for future me */}
        <div className="basis-2/3">
            <div className="mb-6">
                <h1 className="text-3xl font-black text-slate-900 tracking-tight">
                Hi there, <span className="text-lime-600 uppercase">usernameee :3</span>
                </h1>
                <h2 className="text-xl text-slate-500 mt-1">
                ready to bloom?
                </h2>
            </div>

            <div className="">
                <div className="flex gap-1 mb-3">
                    <div className="relative flex-1">
                        <input type="text"
                        placeholder="Search..."
                        className="w-full p-3 bg-slate-50 border-2 border-slate-100 rounded-xl pl-11 pr-5 py-3 text-sm font-semibold text-slate-950 placeholder-slate-600/50
                        focus:outline-none focus:bg-white focus:border-slate-400 focus:ring-4 focus:ring-slate-200/50"/>
                    </div>
                    <button type="button"
                    className="aspect-square p-3 bg-slate-50 border-2 border-slate-100 rounded-xl flex items-center justify-center text-slate-600
                    hover:border-slate-400
                    focus:bg-white focus:border-slate-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0
                        0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
                        </svg>
                    </button>
                    <button type="button"
                    className="aspect-square p-3 bg-slate-50 border-2 border-slate-100 rounded-xl flex items-center justify-center text-slate-600
                    hover:border-slate-400
                    focus:bg-white focus:border-slate-400">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M12 3c2.755
                        0 5.455.232 8.083.678.533.09.917.556.917 1.096v1.044a2.25 2.25
                        0 0 1-.659 1.591l-5.432 5.432a2.25 2.25 0 0 0-.659 1.591v2.927a2.25
                        2.25 0 0 1-1.244 2.013L9.75 21v-6.568a2.25 2.25 0 0 0-.659-1.591L3.659
                        7.409A2.25 2.25 0 0 1 3 5.818V4.774c0-.54.384-1.006.917-1.096A48.32 48.32 0 0 1 12 3Z" />
                        </svg>
                    </button>
                </div>
                <div className="flex flex-col">
                    <Link to="/question"
                    className="flex items-center justify-between p-2 bg-lime-50 rounded-xl">
                        <div className="flex items-center gap-3">
                            <span className="w-6 h-6 text-lime-700 flex items-center justify-center font-bold text-lg">
                                ✓
                            </span>
                            <span className="font-bold text-gray-900">
                                1 - Question 1 name
                            </span>
                        </div>

                        <span className="font-black text-green-600">
                            Easy
                        </span>
                    </Link>

                    <Link to="/question"
                    className="flex items-center justify-between p-2 bg-slate-50 rounded-xl">
                        <div className="flex items-center gap-3">
                            <span className="w-6 h-6 text-lime-700 flex items-center justify-center font-bold text-lg">
                                ✓
                            </span>
                            <span className="font-bold text-gray-900">
                                2 - Question 2 name
                            </span>
                        </div>

                        <span className="font-black text-red-600">
                            Hard
                        </span>
                    </Link>

                    <Link to="/question"
                    className="flex items-center justify-between p-2 bg-lime-50 rounded-xl">
                        <div className="flex items-center gap-3">
                            <span className="w-6 h-6 text-lime-700 flex items-center justify-center font-bold text-lg">
                                
                            </span>
                            <span className="font-bold text-gray-900">
                                3 - Question 3 name
                            </span>
                        </div>

                        <span className="font-black text-yellow-600">
                            Medium
                        </span>
                    </Link>
                </div>
            </div>
        </div>


        <div className="basis-1/3">
            <h1>home page :3</h1>
            <p>meow</p>
            
            <Link to="/profile">
                <button type="button">TEMP: link to profile</button>
            </Link>
        </div>
    </div>
    );
}