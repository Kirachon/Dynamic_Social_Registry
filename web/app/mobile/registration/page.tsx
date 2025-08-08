export default function MobileRegistration(){
  return (
    <div className="max-w-sm mx-auto space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">📱 New Registration</h2>
        <div className="text-sm text-gov-muted">Step 1 of 5</div>
      </header>

      <form className="space-y-3">
        <div>
          <label className="block text-sm text-gov-muted" htmlFor="firstName">First Name *</label>
          <input id="firstName" className="w-full border rounded px-3 py-2" defaultValue="Juan" required />
        </div>
        <div>
          <label className="block text-sm text-gov-muted" htmlFor="lastName">Last Name *</label>
          <input id="lastName" className="w-full border rounded px-3 py-2" defaultValue="Dela Cruz" required />
        </div>
        <div>
          <label className="block text-sm text-gov-muted" htmlFor="philsys">PhilSys Number *</label>
          <div className="flex gap-2">
            <input id="philsys" className="w-full border rounded px-3 py-2" defaultValue="1234-5678-9012-3" required />
            <button type="button" className="px-3 py-2 border rounded text-sm">📷 Scan ID</button>
          </div>
        </div>
        <div>
          <label className="block text-sm text-gov-muted" htmlFor="dob">Date of Birth *</label>
          <input id="dob" type="date" className="w-full border rounded px-3 py-2" />
        </div>
        <fieldset>
          <legend className="block text-sm text-gov-muted">Gender *</legend>
          <div className="flex gap-4">
            <label className="flex items-center gap-2"><input name="gender" type="radio" defaultChecked /> Male</label>
            <label className="flex items-center gap-2"><input name="gender" type="radio" /> Female</label>
            <label className="flex items-center gap-2"><input name="gender" type="radio" /> Other</label>
          </div>
        </fieldset>

        <div className="h-2 bg-gov-bg rounded" aria-label="Progress"><div className="h-2 bg-gov-accent rounded" style={{width:'20%'}} /></div>

        <div className="flex justify-between">
          <button type="button" className="px-3 py-2 border rounded">Back</button>
          <button type="submit" className="px-3 py-2 border rounded bg-gov-accent text-white">Next →</button>
        </div>
      </form>
    </div>
  )
}

