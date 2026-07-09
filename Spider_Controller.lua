-- Spider Patcher: Stable GMEM Version
local track = reaper.GetSelectedTrack(0, 0)
if not track then return end

gfx.init("Spider Patcher", 200, 100)

function Run()
    if gfx.getchar() < 0 then return end
    
    gfx.x = 20; gfx.y = 20
    gfx.drawstr("Spider Patcher")
    
    -- Toggle Button (Writes to gmem memory address 0)
    gfx.rect(20, 40, 100, 30)
    gfx.x = 35; gfx.y = 48; gfx.drawstr("Toggle Hub")
    
    if gfx.mouse_cap == 1 then
        if gfx.mouse_x > 20 and gfx.mouse_x < 120 and gfx.mouse_y > 40 and gfx.mouse_y < 70 then
            -- Flip the bit in shared memory
            local current = reaper.gmem_read(0)
            reaper.gmem_write(0, current > 0.5 and 0 or 1)
            reaper.sleep(200) -- Safety delay
        end
    end
    
    gfx.update()
    reaper.defer(Run)
end
Run()
