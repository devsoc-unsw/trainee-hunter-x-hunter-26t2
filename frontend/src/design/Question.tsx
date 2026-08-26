import { Link } from 'react-router-dom';

export default function Question() {
    return (
    <div>
        <h1>question page :3</h1>
        <p>meow</p>
        
        <Link to="/">
            <button type="button">Go home</button>
        </Link>
    </div>
    );
}