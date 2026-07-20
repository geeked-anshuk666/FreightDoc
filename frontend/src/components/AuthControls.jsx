import {Show,UserButton} from '@clerk/react';
export default function AuthControls(){if(!import.meta.env.VITE_CLERK_PUBLISHABLE_KEY)return null;return <div className="auth-controls"><Show when="signed-out"><a href="/sign-in">Sign in</a><a className="nav-create" href="/sign-up">Create account</a></Show><Show when="signed-in"><UserButton/></Show></div>}
