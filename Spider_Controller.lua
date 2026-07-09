-- Spider Patcher: Ultra-Stable Version
local track = reaper.GetSelectedTrack(0, 0)
if not track then 
    reaper.ShowMessageBox("Select a track first!", "Spider", 0) 
    return 
end

-- UI Settings
local window_name = "Spider Patcher"
gfx.init(window_name, 400, 300)

function Run()
    -- Only update if the window is open
    if gfx.getchar() < 0 then return end 

    -- Draw UI
    gfx.x = 20; gfx.y = 20
    gfx.drawstr("Spider Patch Editor")
    
    -- Button: Toggle Hub
    gfx.rect(20, 50, 100, 30)
    gfx.x = 35; gfx.y = 58; gfx.drawstr("Toggle Hub")
    
    -- Button: Export
    gfx.rect(20, 100, 100, 30)
    gfx.x = 35; gfx.y = 108; gfx.drawstr("Export .spdr")

    -- Click Detection with Debounce (Prevents API Flooding)
    if gfx.mouse_cap == 1 then
        if gfx.mouse_x > 20 and gfx.mouse_x < 120 then
            -- Toggle Logic
            if gfx.mouse_y > 50 and gfx.mouse_y < 80 then
                local fx = reaper.TrackFX_GetByName(track, "Spider Router Hub", false)
                if fx >= 0 then
                    local state = reaper.TrackFX_GetParam(track, fx, 0)
                    reaper.TrackFX_SetParam(track, fx, 0, state < 0.5 and 1 or 0)
                end
                reaper.sleep(100) -- Small delay to prevent API spamming
            -- Export Logic
            elseif gfx.mouse_y > 100 and gfx.mouse_y < 130 then
                local f = io.open(reaper.GetResourcePath() .. "/Spider_Patch.spdr", "w")
                if f then f:write("SPIDER_PATCH_DATA\n") f:close() end
                reaper.sleep(100)
            end
        end
    end

    -- Update display and defer
    gfx.update()
    reaper.defer(Run)
end

Run()
