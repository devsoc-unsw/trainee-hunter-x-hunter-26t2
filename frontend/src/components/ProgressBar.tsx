// import { Link } from 'react-router-dom'
// import { useAuth } from '../auth/AuthContext'

export default function ProgressBar() {
    // const { me } = useAuth()

    const stats = {
    solved: 3,
    total: 4041,
    attempting: 20,
    easy: { solved: 3, total: 962 },
    medium: { solved: 200, total: 2109 },
    hard: { solved: 5, total: 970 }
    }


    const radius = 52
    const circumference = 2 * Math.PI * radius

    const gapAngle = 12 
    const gapLength = (gapAngle / 360) * circumference 

    const segmentLength = (circumference - 3 * gapLength) / 3


    const getSegmentStyles = (solved: number, total: number, segmentIndex: number) => {
        // Calculate percentage solved for this difficulty
        const pct = total > 0 ? Math.min(solved / total, 1) : 0
        const filledLength = pct * segmentLength

        const segmentStartOffset = -segmentIndex * (segmentLength + gapLength)

        return {
        bgDasharray: `${segmentLength} ${circumference - segmentLength}`,
        fillDasharray: `${filledLength} ${circumference - filledLength}`,
        dashOffset: segmentStartOffset,
        }
    }

    const easyStyles = getSegmentStyles(stats.easy.solved, stats.easy.total, 0)
    const medStyles = getSegmentStyles(stats.medium.solved, stats.medium.total, 1)
    const hardStyles = getSegmentStyles(stats.hard.solved, stats.hard.total, 2)

    return (
        <div className="flex flex-row items-center gap-6">
            {/* lhs */}
            <div className="relative w-44 h-44 flex items-center justify-center">
                {/* progress bar */}
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={easyStyles.bgDasharray}
                    strokeDashoffset={easyStyles.dashOffset}
                    strokeLinecap="round"
                    className="stroke-green-50 stroke-8 fill-transparent"
                    />
                    {/* Easy Solid Fill */}
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={easyStyles.fillDasharray}
                    strokeDashoffset={easyStyles.dashOffset}
                    strokeLinecap="round"
                    className="stroke-green-500 stroke-8 fill-transparent"
                    />

                    {/* medium */}
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={medStyles.bgDasharray}
                    strokeDashoffset={medStyles.dashOffset}
                    strokeLinecap="round"
                    className="stroke-yellow-50 stroke-8 fill-transparent"/>
                    {/* Medium Solid Fill */}
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={medStyles.fillDasharray}
                    strokeDashoffset={medStyles.dashOffset}
                    strokeLinecap="round"
                    className="stroke-yellow-500 stroke-8 fill-transparent"/>

                    {/* hard */}
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={hardStyles.bgDasharray}
                    strokeDashoffset={hardStyles.dashOffset}
                    strokeLinecap="round"
                    className="stroke-red-50 stroke-8 fill-transparent"/>
                    <circle
                    cx="60"
                    cy="60"
                    r={radius}
                    strokeDasharray={hardStyles.fillDasharray}
                    strokeDashoffset={hardStyles.dashOffset}
                    strokeLinecap="round"
                    // animations would be nice
                    className="stroke-red-500 stroke-8 fill-transparent"/>
                </svg>

                {/* Center Text Readout */}
                <div className="absolute flex flex-col items-center justify-center text-center">
                    <div className="flex items-baseline">
                    <span className="text-3xl font-black text-slate-900">{stats.solved}</span>
                    <span className="text-sm font-bold text-slate-400">/{stats.total}</span>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-bold text-lime-600 mt-0.5">
                    <span>✓</span> Solved
                    </div>
                    {stats.attempting > 0 && (
                    <span className="text-[11px] font-medium text-slate-400 mt-1">
                        {stats.attempting} Attempting
                    </span>
                    )}
                </div>
            </div>
            {/* rhs */}
            <div className="flex-1 flex flex-col gap-3">
                <div className="flex flex-col gap-3 flex-1">
                    {/* Easy */}
                    <div className="bg-green-50 border-2 border-green-200 rounded-xl p-2 text-center">
                    <span className="text-xs font-bold text-green-600 block">Easy</span>
                    <span className="text-sm font-black text-slate-800">
                        {stats.easy.solved}/{stats.easy.total}
                    </span>
                    </div>

                    {/* Medium */}
                    <div className="bg-yellow-50 border-2 border-yellow-200 rounded-xl p-2 text-center">
                    <span className="text-xs font-bold text-yellow-500 block">Med.</span>
                    <span className="text-sm font-black text-slate-800">
                        {stats.medium.solved}/{stats.medium.total}
                    </span>
                    </div>

                    {/* Hard */}
                    <div className="bg-red-50 border-2 border-red-200 rounded-xl p-2 text-center">
                    <span className="text-xs font-bold text-red-500 block">Hard</span>
                    <span className="text-sm font-black text-slate-800">
                        {stats.hard.solved}/{stats.hard.total}
                    </span>
                    </div>
                </div>
            </div>
        </div>
    )
}
