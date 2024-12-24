def end_session(sessions, user):
    
    if user not in sessions:
        return sessions
    session = sessions[user]
    
    if session["ref_count"] == 0:
        return sessions
    else:
        if session["ref_count"] == 1:
            session["ref_count"] =0
            session["closed"] = True
            return sessions

        else :
            session["ref_count"] = session["ref_count"] - 1
            session["closed"] = False
            return sessions
        
        

  
    
    