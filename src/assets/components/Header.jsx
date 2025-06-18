import { Link, Route, Router, Switch } from "wouter-preact";
import IconSearch from '~icons/nippy/search';

export function Header() {
  return (
    <header>
      <nav>
        <ul>
          <li>
            <strong>
              <Link href="/">
                <span className="logo"></span>
              </Link>
            </strong>
          </li>
        </ul>
        <ul className="s-container">
          <li className="s-form">
            <form action="/results" method="get">
              <input
                type="search"
                name="search_query"
                id="search_query"
                className="input"
                value=""
              />
              <button className="btn secondary">
                <div><IconSearch style={{fontSize: '1rem'}}/></div>
                
              </button>
            </form>
          </li>

          <li>
            <button className="btn secondary">
              Upload
            </button>
          </li>
        </ul>

        <ul>
          <li>
            <button className="btn primary">Sign in</button>
          </li>
          <li>
            <button className="btn secondary">Sign out</button>
          </li>
        </ul>
      </nav>
    </header>
  );
}
