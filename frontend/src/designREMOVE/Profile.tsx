import { Link } from 'react-router-dom';

export default function Profile() {
    return (
    <div>
        <h1>profile page :3</h1>
        <p>meow</p>
        
        <Link to="/">
            <button type="button">Go home</button>
        </Link>
    </div>
    );
}