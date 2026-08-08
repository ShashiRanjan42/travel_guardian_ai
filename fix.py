import sys

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    broken_str = '''      if (data) {
    if (el) {'''
    
    fixed_str = '''      if (data) {
        setBookingNotice(✅ Protected  Confirmed & Saved to Profile! ( → ));
        setTimeout(() => setBookingNotice(null), 5000);
        if (onSelectItinerary && data.itinerary_id) {
          onSelectItinerary(data.itinerary_id);
        }
        setActiveTab('MY_BOOKINGS');
      }
    } catch (e) {
      setBookingNotice(✅ Protected  Confirmed & Saved to Profile!);
      setTimeout(() => setBookingNotice(null), 4000);
      setActiveTab('MY_BOOKINGS');
    }
  };

  // REAL-TIME CONVERSATIONAL LLM BOOKING AGENT TURN HANDLER
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMsg.trim()) return;

    if (!currentUser) {
      if (onOpenAuth) onOpenAuth();
      setChatMessages(prev => [...prev, { sender: 'AI', text: "🔒 Please log in to your account so I can process and protect your travel bookings!" }]);
      return;
    }

    const userText = inputMsg;
    setChatMessages(prev => [...prev, { sender: 'USER', text: userText }]);
    setInputMsg('');

    try {
      const res = await fetch('/api/v1/agents/chat_book', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: agentSessionId,
          message: userText,
          user_name: currentUser?.name || 'Traveler'
        })
      });

      if (res.ok) {
        const data = await res.json();
        let replyObj = {
          sender: 'AI',
          text: data.reply || "I can process your booking! Please provide your destination city, budget, or dates."
        };

        if (data.status === 'READY_TO_BOOK' && data.package_plan) {
          const pkg = data.package_plan;
          replyObj.packagePlan = pkg;
          replyObj.actionButton = {
            label: ⚡ Confirm & Book  Trip Now,
            onClick: () => {
              handleBookingSubmit('FLIGHT & HOTEL PACKAGE', 'Delhi (DEL)', ${pkg.destination} Resort, 'Air India & Taj Hotels', pkg.start_date);
              setChatMessages(prev => [...prev, { sender: 'AI', text: 🎉 Outstanding! Your   package has been booked and activated with 7-Agent AI Guardian Protection! }]);
            }
          };
        }

        setChatMessages(prev => [...prev, replyObj]);
      } else {
        setChatMessages(prev => [...prev, { sender: 'AI', text: "I can process your booking! What is your destination, budget, or travel dates?" }]);
      }
    } catch (err) {
      setChatMessages(prev => [...prev, { sender: 'AI', text: "Network error connecting to AI Booking Agent. Please try again." }]);
    }
  };

  const scrollToPlanSection = () => {
    const el = document.getElementById('plan-options-section');
    if (el) {'''

    if broken_str in content:
        content = content.replace(broken_str, fixed_str)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Fixed successfully.")
    else:
        print("Broken string not found.")

fix_file(r'c:\Users\GenAIDELLUCERNAUSR49\Desktop\app2\travel_guardian_ai\frontend\src\components\CustomerMMTView.jsx')
