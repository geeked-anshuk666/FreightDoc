export default function WarningPanel({errors}){return errors.length?<section className="warning"><h2>Review warnings</h2>{errors.map((e,i)=><p key={i}>{e.issue} Fix: {e.fix}</p>)}</section>:null}
