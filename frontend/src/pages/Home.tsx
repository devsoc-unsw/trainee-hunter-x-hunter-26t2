import { Link } from 'react-router-dom';
import Problems from './Problems';
import { useAuth } from '../auth/AuthContext';
import Keyboard from '../components/Keyboard';

export default function Home() {
    const { me } = useAuth()
    return (
    <div className="m-6 flex flex-row gap-5">
        {/* im gonna need a header here but thats an issue for future me */}
        <div className="basis-2/3">
            <div className="mb-6">
                <h1 className="text-3xl font-black text-slate-900 tracking-tight">
                Hi there, <span className="text-lime-600 uppercase">{me?.username ?? 'stranger'}</span>
                </h1>
                <h2 className="text-xl text-slate-500 mt-1">
                ready to bloom?
                </h2>
            </div>
            {/* ideally id like to show the problems that they have already as a work in progress */}
            <Problems />

            <Link to="/problems"  className= "p-3 bg-lime-600 text-white font-bold rounded-xl hover:bg-lime-700">
            View All Problems
            </Link>
        </div>


        <div className="basis-1/3">
            <p className="text-2xl font-black text-slate-900">Your keyboard</p>
            <div className="w-full p-4">
                <Keyboard unlockedCount={17}/>
            </div>
        </div>
    </div>
    );
}