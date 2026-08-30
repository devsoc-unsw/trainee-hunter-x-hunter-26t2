import { Link } from 'react-router-dom';
import Problems from './Problems';

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
            <Problems />

            <Link to="/problems"  className= "p-3 bg-lime-600 text-white font-bold rounded-xl hover:bg-lime-700">
            View All Problems
            </Link>
        </div>


        <div className="basis-1/3">
            <div className="bg-red-100">
                keyboard here
            </div>
        </div>
    </div>
    );
}