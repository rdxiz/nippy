import { Header } from "./Header";
import { Layout } from "./Layout";
export function App() {
  return (<>
  <Header />
  <main>
    <Layout content={(<p>aaaaa</p>)}/>
    
  </main>
  </>);
}
