import { useNavigate } from 'react-router-dom'
import Keyboard from '../components/Keyboard'

export default function Landing() {
    const navigate = useNavigate()
// i totally did not copy this from the leetcode landing page :grin: :grin:
    return (
        <div className="bg-slate-50 flex flex-col justify-between p-6 md:p-12 text-slate-800">
            <section className="max-w-4xl mx-auto text-center flex flex-col items-center gap-6 my-8">
                <h1 className="text-4xl md:text-6xl font-black text-slate-900 tracking-tight leading-tight">
                A new way to learn, <br className="hidden sm:inline" />
                <span className="text-lime-600">one keystroke at a time.</span>
                </h1>

                <p className="text-lg md:text-xl text-slate-600 max-w-2xl font-medium">
                    Solve coding challenges, collect coins, and build your new typing garden!
                </p>

                {/* Primary Call to Action */}
                <div className="flex flex-col sm:flex-row items-center gap-4 mt-2 w-full sm:w-auto">
                <button
                    onClick={() => navigate('/signup')}
                    className="w-full sm:w-auto px-8 py-3.5 bg-lime-500 hover:bg-lime-600 text-white font-black text-lg rounded-xl border-2 border-lime-600 transition-all transform hover:-translate-y-0.5 cursor-pointer">
                    Create account
                </button>
                <button
                    onClick={() => navigate('/login')}
                    className="w-full sm:w-auto px-8 py-3.5 bg-white hover:bg-slate-100 text-slate-700 font-bold text-lg rounded-2xl border-2 border-slate-200 transition-all cursor-pointer">
                    Sign In
                </button>
                </div>
            </section>

            {/* 2. Key Features Cards */}
            <section className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 my-8 w-full">
                <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 flex flex-col gap-3">
                    <h3 className="text-xl font-black text-slate-900">Solve Problems</h3>
                    <p className="text-slate-600 text-sm font-medium">
                        Get the most out of Keebloom by providing structure to guide your progress towards the next step in your programming career.
                    </p>
                </div>

                <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 flex flex-col gap-3">
                    <h3 className="text-xl font-black text-slate-900">Earn Coins</h3>
                    <p className="text-slate-600 text-sm font-medium">
                        Get rewarded for every correct submission and the keys you press!
                    </p>
                </div>

                <div className="bg-white p-6 rounded-2xl border-2 border-slate-200 flex flex-col gap-3">
                    <h3 className="text-xl font-black text-slate-900">Customize Gear</h3>
                    <p className="text-slate-600 text-sm font-medium">
                        Spend coins in the shop to unlock custom keycaps.
                    </p>
                </div>
            </section>

            <section className="max-w-4xl mx-auto w-full my-8">
                <div className="bg-white p-6 rounded-3xl border-2 border-slate-200 shadow-sm flex flex-col gap-4">
                <div className="w-full bg-slate-50 p-4 rounded-2xl border-2 border-slate-200">
                    <Keyboard unlockedCount={26} />
                </div>
                </div>
            </section>

            <footer className="text-center text-slate-400 text-sm font-semibold mt-12">
                Ready to bloom? <button onClick={() => navigate('/signup')} className="text-lime-600 hover:underline">Create an account</button>
            </footer>
        </div>
    )
}