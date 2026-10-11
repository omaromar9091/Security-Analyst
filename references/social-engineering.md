# Human & Attack Vectors

Use this file for assessing a message, call, or scenario suspected of being social engineering, or for gauging how aware a team or organization is of these risks.

## The Psychological Principles Being Exploited

Most social engineering leans on one or more of these.

Authority: posing as an official, a manager, or technical support so the target doesn't push back with questions. Urgency: time pressure ("your account locks in an hour") that short-circuits verification. Scarcity: a limited offer that vanishes without an immediate response. Familiarity: pretending to already know the target, or to have a personal connection, to lower their guard. Commitment and consistency: a small agreement first, with a bigger ask built on top of it. Social proof: the implication that "your colleagues already did this."

## Common Attack Patterns

**Phishing**: email or text claiming to be from somewhere trusted, pushing for credentials or a click on a malicious link or attachment. Spear phishing is the same idea aimed at one person or organization, built with real details about them so it lands harder.

**Vishing**: phishing over a phone call, usually posing as technical or banking support.

**Pretexting**: a full story built around getting trust — a new employee, an inspector, a vendor — to extract information or access.

**Baiting**: a dropped USB drive, or a file left somewhere appealing, counting on the target to open it themselves.

**Tailgating**: getting into a physically secured space through ordinary social behavior — hands full of boxes, a forgotten badge — rather than a technical break-in.

**BEC**: an executive's email, impersonated or actually compromised, used to issue a transfer or a data request that looks legitimate on its face.

## Warning Signs Worth Flagging

A request that doesn't fit how this relationship normally works — a manager asking for a transfer over WhatsApp, say. Pressure to move fast and skip verifying through another channel. A link or address close to the real one but with a small difference, the classic typosquat. A request for something — a password, a verification code, card details — that would never normally be asked for this way. An attachment or link from an expected sender but in a format or context that's off.

## Assessing a Scenario or Message

1. Work out which of the psychological levers above is doing the work here.
2. Compare the channel and the approach against how this kind of request normally happens inside the organization.
3. Check what's technically verifiable — the real sender address, where a link actually points, the domain behind it.
4. Weigh severity by what's actually being asked for, not just by how many red flags are present.
5. Suggest an independent check — calling the person on a number already on file, not the one the message supplies — before anything sensitive happens.

## When Explaining This to a User

Point to the specific indicators behind the call, not a general sense that something feels off. If the ask is about measuring a team's awareness, suggest training or a simulated phishing exercise as the way to test it, never deceiving people without the people running the program knowing about it.

## Worked Examples

**Input**: An employee gets an email that looks like it's from the CEO, sent from a lookalike domain — the real one is company.com, this one is conpany.com — asking for an urgent wire transfer to a new vendor before end of day, with a note to "handle this quietly, I'm in back-to-back meetings."

**Analysis**: Three levers at once here. Authority (posing as the CEO), urgency (before end of day), and isolation ("handle this quietly" is specifically there to head off anyone checking with a colleague). The domain is a concrete tell — one swapped letter, easy to miss at a glance. A money request paired with a fabricated reason to skip the normal approval process and a spoofed sender is the shape of a BEC attempt, not a routine ask.

**Output**: Assessment: high-confidence BEC attempt. Red flags: a one-character typosquat of the real domain, a request that bypasses the standard payment process, and "handle this quietly" framing built specifically to prevent the verification step that would otherwise catch it. Recommended action: don't act on it, call the CEO directly on a number already on file rather than anything in the email, and report it so the lookalike domain can get blocked.

---

**Input**: A caller claims to be from "IT support," says there's a security issue with the employee's account, and asks them to read out the one-time passcode that just arrived by text so IT can "verify the account."

**Analysis**: Legitimate IT support has no reason to ask for a one-time passcode — the entire point of one is that only the account holder ever enters it, directly in the login flow. Asking for it over the phone is an attempt to hijack an MFA-protected login in real time, and the manufactured "security issue" is there to make an unusual request feel justified.

**Output**: Assessment: vishing aimed at an MFA bypass. The request itself is the tell — no real support process ever needs someone to read a passcode out loud. Recommended action: end the call, don't share the code, and report it so the team can check whether others got similar calls. If training is the goal, this is a strong candidate for a simulated vishing exercise, run with security sign-off.

---

**Input**: A new hire gets a LinkedIn message from someone claiming to be a recruiter at a partner company. After some friendly back-and-forth, the person asks for a copy of an internal org chart "to help coordinate an upcoming project."

**Analysis**: The friendly exchange before the actual ask is the liking-and-commitment pattern — rapport and small agreements first make a bigger, odder request feel reasonable by the time it shows up. An org chart is reconnaissance material: names, reporting lines, who to impersonate later for a more convincing pretext. And the channel doesn't match the sensitivity of what's being asked — nobody shares internal structure with an external contact over social media as a matter of course.

**Output**: Assessment: likely pretexting or reconnaissance rather than an immediate ask for money or credentials — more a setup for something later. The mismatch between the casual channel and the sensitivity of the request is the giveaway. Recommended action: don't share the chart, verify the recruiter and the partnership through an official channel if it's real, and flag the interaction to security given what was being sought.
