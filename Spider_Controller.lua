-- Spider Patcher UI
local track = reaper.GetSelectedTrack(0, 0)
if not track then reaper.ShowMessageBox("Select a track!", "Spider", 0) return end

function SavePatch(filename)
    local f = io.open(filename, "w")
    if f then f:write("SPIDER_PATCH_DATA\n") f:close() end
end

function Draw()
    gfx.init("Spider Patcher", 400, 300)
    while gfx.getchar() >= 0 do
        gfx.x = 20; gfx.y = 20
        gfx.drawstr("Spider Patch Editor")
        
        -- Toggle Button
        gfx.rect(20, 50, 100, 30)
        gfx.x = 35; gfx.y = 58
        gfx.drawstr("Toggle Hub")
        
        if gfx.mouse_cap == 1 and gfx.mouse_x > 20 and gfx.mouse_x < 120 and gfx.mouse_y > 50 and gfx.mouse_y < 80 then
            local fx = reaper.TrackFX_GetByName(track, "Spider Router Hub", false)
            local state = reaper.TrackFX_GetParam(track, fx, 0)
            reaper.TrackFX_SetParam(track, fx, 0, state == 0 and 1 or 0)
        end

        -- Export Button
        gfx.rect(20, 100, 100, 30)
        gfx.x = 35; gfx.y = 108
        gfx.drawstr("Export .spdr")
        
        if gfx.mouse_cap == 1 and gfx.mouse_x > 20 and gfx.mouse_y > 100 and gfx.mouse_y < 130 then
            SavePatch(reaper.GetResourcePath() .. "/Spider_Patch.spdr")
            reaper.ShowMessageBox("Saved as Spider_Patch.spdr", "Success", 0)
        end
        
        gfx.update()
    end
end
Draw()
